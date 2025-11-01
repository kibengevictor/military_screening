import os
import numpy as np
import pandas as pd
import tensorflow as tf
import joblib
import pickle
import io
import csv
from datetime import datetime
import kg
from flask import Flask, render_template, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'uploads'

ALLOWED_EXTENSIONS = {'csv'}

# Create upload folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variables for loaded components
model = None
scaler = None
label_encoder = None
knowledge_graph = None
all_components_loaded = False

def allowed_file(filename):
    """Check if uploaded file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_default_knowledge_graph():
    """Create a default knowledge graph if loading fails"""
    logger.info("🔄 Creating default knowledge graph...")
    
    class DefaultKnowledgeGraph:
        def __init__(self):
            self.rules = {
                'high_confidence': ['Infantry', 'Special Forces', 'Combat Engineer'],
                'medium_confidence': ['Military Police', 'Logistics', 'Signals'],
                'low_confidence': ['Medical Evaluation Required']
            }
        
        def get_recommendations(self, confidence):
            if confidence > 0.8:
                return self.rules['high_confidence']
            elif confidence > 0.6:
                return self.rules['medium_confidence']
            else:
                return self.rules['low_confidence']
        
        def recommend_roles(self, biomarkers):
            """Compatibility method for knowledge graph interface"""
            confidence = biomarkers.get('movement_quality', 0.5)
            return {
                'recommended_roles': self.get_recommendations(confidence),
                'detected_risks': [],
                'contraindicated_roles': []
            }
    
    return DefaultKnowledgeGraph()

def ensure_model_exists():
    """Ensure model file exists and extract if needed"""
    if not os.path.exists("military_screening_cnn.h5"):
        logger.info("🔄 Model file not found, extracting from 7z...")
        try:
            import py7zr
            if os.path.exists("military_screening_cnn.7z"):
                with py7zr.SevenZipFile('military_screening_cnn.7z', mode='r') as z:
                    z.extractall()
                logger.info("✅ Model extracted from 7z successfully!")
                return True
            else:
                logger.error("❌ 7z file not found!")
                return False
        except Exception as e:
            logger.error(f"❌ Extraction failed: {e}")
            return False
    return True

def load_all_components():
    """Load all AI components with proper error handling"""
    global model, scaler, label_encoder, knowledge_graph, all_components_loaded
    
    try:
        logger.info("🚀 STARTING COMPONENT LOADING PROCESS...")
        
        # Step 1: Ensure model exists
        if not ensure_model_exists():
            logger.error("❌ Failed to ensure model exists")
            return False
        
        # Step 2: Load TensorFlow model
        logger.info("🔄 Loading TensorFlow model...")
        model = tf.keras.models.load_model("military_screening_cnn.h5")
        logger.info("✅ TensorFlow model loaded")
        
        # Step 3: Load scaler
        logger.info("🔄 Loading scaler...")
        scaler = joblib.load("scaler.pkl")
        logger.info("✅ Scaler loaded")
        
        # Step 4: Load label encoder
        logger.info("🔄 Loading label encoder...")
        label_encoder = joblib.load("label_encoder.pkl")
        logger.info("✅ Label encoder loaded")
        
        # Step 5: Try to load knowledge graph
        logger.info("🔄 Loading knowledge graph...")
        try:
            knowledge_graph = joblib.load("military_knowledge_graph.pkl")
            logger.info("✅ Knowledge graph loaded from file")
        except Exception as e:
            logger.warning(f"⚠️ Knowledge graph loading failed: {e}")
            try:
                class FixUnpickler(pickle.Unpickler):
                    def find_class(self, module, name):
                        if module == "__main__" and name == "MilitaryScreeningKG":
                            return getattr(kg, "MilitaryScreeningKG")
                        return super().find_class(module, name)

                with open("military_knowledge_graph.pkl", "rb") as f:
                    knowledge_graph = FixUnpickler(f).load()
                logger.info("✅ Knowledge graph loaded via FixUnpickler")
            except Exception as e2:
                logger.warning(f"⚠️ FixUnpickler failed: {e2}")
                knowledge_graph = create_default_knowledge_graph()
                logger.info("✅ Default knowledge graph created")
        
        # Verify critical components
        critical_components_loaded = all([model, scaler, label_encoder])
        if critical_components_loaded:
            all_components_loaded = True
            logger.info("🎯 CRITICAL COMPONENTS LOADED - SYSTEM READY!")
            return True
        else:
            logger.error("❌ Critical components failed to load")
            return False
            
    except Exception as e:
        logger.error(f"❌ CRITICAL ERROR loading components: {e}")
        all_components_loaded = False
        return False

def extract_biomarkers(confidence, activity_name):
    """Extract military biomarkers from prediction"""
    biomarkers = {
        'movement_quality': float(confidence),
        'fatigue_index': 0.05 if confidence > 0.8 else 0.15,
        'movement_smoothness': float(confidence * 0.9 + 0.1)
    }
    
    # Add activity-specific scores
    if activity_name in ['WALKING', 'WALKING_UPSTAIRS', 'WALKING_DOWNSTAIRS']:
        biomarkers['dynamic_power_score'] = float(confidence * 0.95)
    
    return biomarkers

def make_military_decision(confidence, biomarkers):
    """Make military screening decision based on biomarkers"""
    if confidence > 0.8:
        decision = "PASS"
        reason = "Excellent movement quality and physical performance"
        risk_level = "LOW"
    elif confidence > 0.6:
        decision = "CONDITIONAL PASS"
        reason = "Adequate performance with some areas for improvement"
        risk_level = "MODERATE"
    else:
        decision = "FAIL"
        reason = "Movement analysis indicates physical limitations"
        risk_level = "HIGH"
    
    return decision, reason, risk_level

def process_single_candidate(sensor_data_array, candidate_id=None):
    """Process a single candidate's sensor data"""
    try:
        # Validate input
        if len(sensor_data_array) != 561:
            return {
                'success': False,
                'candidate_id': candidate_id,
                'error': f'Expected 561 features, got {len(sensor_data_array)}'
            }
        
        # Reshape for processing
        sensor_array = np.array(sensor_data_array, dtype=np.float64).reshape(1, -1)
        
        # Preprocess
        try:
            if hasattr(scaler, 'feature_names_in_'):
                cols = list(scaler.feature_names_in_)
                if len(cols) != sensor_array.shape[1]:
                    cols = [f'feature_{i}' for i in range(sensor_array.shape[1])]
            else:
                cols = [f'feature_{i}' for i in range(sensor_array.shape[1])]
            
            sensor_df = pd.DataFrame(sensor_array, columns=cols)
            scaled_data = scaler.transform(sensor_df)
        except Exception:
            scaled_data = scaler.transform(sensor_array)
        
        reshaped_data = scaled_data.reshape(1, 561, 1)
        
        # Make prediction
        predictions = model.predict(reshaped_data, verbose=0)
        confidence = float(np.max(predictions))
        predicted_class = int(np.argmax(predictions, axis=1)[0])
        activity = label_encoder.inverse_transform([predicted_class])[0]
        
        # Extract biomarkers
        biomarkers = extract_biomarkers(confidence, activity)
        
        # Get role recommendations from knowledge graph
        try:
            if hasattr(knowledge_graph, 'recommend_roles'):
                kg_result = knowledge_graph.recommend_roles(biomarkers)
                roles = kg_result['recommended_roles']
                detected_risks = kg_result.get('detected_risks', [])
            else:
                roles = knowledge_graph.get_recommendations(confidence)
                detected_risks = []
        except Exception as e:
            logger.warning(f"KG recommendation failed: {e}, using fallback")
            if confidence > 0.8:
                roles = ["Infantry", "Special Forces", "Combat Engineer"]
            elif confidence > 0.6:
                roles = ["Military Police", "Logistics", "Signals"]
            else:
                roles = ["Medical Evaluation Required"]
            detected_risks = []
        
        # Make decision
        decision, reason, risk_level = make_military_decision(confidence, biomarkers)
        
        return {
            'success': True,
            'candidate_id': candidate_id or 'Unknown',
            'activity': activity,
            'confidence': confidence,
            'decision': decision,
            'reason': reason,
            'risk_level': risk_level,
            'recommended_roles': roles,
            'detected_risks': detected_risks,
            'biomarkers': biomarkers,
            'performance_score': round(confidence * 100, 1)
        }
        
    except Exception as e:
        logger.error(f"Error processing candidate {candidate_id}: {e}")
        return {
            'success': False,
            'candidate_id': candidate_id or 'Unknown',
            'error': str(e)
        }

# ==================== ROUTES ====================

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/health')
def health_check():
    """Detailed health check endpoint"""
    component_status = {
        'model_loaded': model is not None,
        'scaler_loaded': scaler is not None,
        'label_encoder_loaded': label_encoder is not None,
        'knowledge_graph_loaded': knowledge_graph is not None,
        'all_components_ready': all_components_loaded
    }
    
    status = 'healthy' if all_components_loaded else 'initializing'
    
    return jsonify({
        'status': status,
        'components': component_status,
        'message': 'Military AI Screening System',
        'system_ready': all_components_loaded
    })

@app.route('/predict', methods=['POST', 'OPTIONS'])
def predict():
    """Single candidate prediction endpoint"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        if not all_components_loaded:
            return jsonify({
                'success': False, 
                'error': 'System is still initializing. Please wait and try again.'
            })
        
        # Get and validate request data
        data = request.get_json()
        if not data or 'sensor_data' not in data:
            return jsonify({'success': False, 'error': 'No sensor_data provided'})
        
        sensor_data = data['sensor_data']
        candidate_id = data.get('candidate_id', 'Demo')
        
        # Process candidate
        result = process_single_candidate(sensor_data, candidate_id)
        
        if result['success']:
            logger.info(f"✅ Prediction for {candidate_id}: {result['activity']} ({result['confidence']:.3f})")
        
        # Format response for frontend
        return jsonify({
            'success': result['success'],
            'prediction': {
                'activity': result.get('activity', 'N/A'),
                'confidence': result.get('confidence', 0),
                'decision': result.get('decision', 'UNKNOWN'),
                'reason': result.get('reason', 'Processing error'),
                'risk_level': result.get('risk_level', 'UNKNOWN'),
                'recommended_roles': result.get('recommended_roles', []),
                'detected_risks': result.get('detected_risks', []),
                'performance_score': result.get('performance_score', 0),
                'biomarkers': result.get('biomarkers', {})
            }
        } if result['success'] else result)
        
    except Exception as e:
        logger.error(f"❌ Prediction endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/batch-predict', methods=['POST'])
def batch_predict():
    """Batch CSV prediction endpoint"""
    try:
        if not all_components_loaded:
            return jsonify({
                'success': False,
                'error': 'System is still initializing.'
            })
        
        # Check if file was uploaded
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file uploaded'})
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Only CSV files are allowed'})
        
        logger.info(f"📁 Processing CSV file: {file.filename}")
        
        # Read CSV
        df = pd.read_csv(file)
        logger.info(f"CSV shape: {df.shape}")
        
        # Validate structure
        if df.shape[1] < 561:
            return jsonify({
                'success': False,
                'error': f'CSV must have at least 561 feature columns. Found: {df.shape[1]}'
            })
        
        # Check for candidate ID column
        has_id = 'candidate_id' in df.columns or 'id' in df.columns
        
        if has_id:
            id_col = 'candidate_id' if 'candidate_id' in df.columns else 'id'
            candidate_ids = df[id_col].tolist()
            feature_cols = [col for col in df.columns if col != id_col][:561]
        else:
            candidate_ids = [f"Candidate_{i+1:03d}" for i in range(len(df))]
            feature_cols = df.columns[:561].tolist()
        
        # Process all candidates
        results = []
        for idx in range(len(df)):
            sensor_data = df.iloc[idx][feature_cols].values
            candidate_id = candidate_ids[idx]
            
            result = process_single_candidate(sensor_data, candidate_id)
            results.append(result)
        
        # Calculate summary
        successful = [r for r in results if r.get('success', False)]
        pass_count = sum(1 for r in successful if 'PASS' in r.get('decision', ''))
        fail_count = len(successful) - pass_count
        
        summary = {
            'total_candidates': len(results),
            'successful_screenings': len(successful),
            'failed_screenings': len(results) - len(successful),
            'pass_count': pass_count,
            'fail_count': fail_count,
            'pass_rate': round((pass_count / len(successful) * 100), 1) if successful else 0
        }
        
        logger.info(f"✅ Batch processing complete: {len(results)} candidates")
        
        return jsonify({
            'success': True,
            'summary': summary,
            'results': results
        })
        
    except Exception as e:
        logger.error(f"❌ Batch prediction error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download-template')
def download_template():
    """Download CSV template for batch screening"""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        header = ['candidate_id'] + [f'feature_{i}' for i in range(561)]
        writer.writerow(header)
        
        # Sample rows with realistic data
        for i in range(5):
            row = [f'CANDIDATE_{i+1:03d}'] + list(np.random.randn(561))
            writer.writerow(row)
        
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='military_screening_template.csv'
        )
        
    except Exception as e:
        logger.error(f"Template download error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/download-results', methods=['POST'])
def download_results():
    """Download screening results as CSV"""
    try:
        data = request.json
        results = data.get('results', [])
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow([
            'Candidate ID', 'Activity', 'Confidence', 'Decision',
            'Risk Level', 'Reason', 'Recommended Roles',
            'Movement Quality', 'Fatigue Index', 'Movement Smoothness', 'Performance Score'
        ])
        
        # Data rows
        for result in results:
            if result.get('success', False):
                biomarkers = result.get('biomarkers', {})
                writer.writerow([
                    result.get('candidate_id', 'N/A'),
                    result.get('activity', 'N/A'),
                    f"{result.get('confidence', 0):.3f}",
                    result.get('decision', 'N/A'),
                    result.get('risk_level', 'N/A'),
                    result.get('reason', 'N/A'),
                    ', '.join(result.get('recommended_roles', [])),
                    f"{biomarkers.get('movement_quality', 0):.3f}",
                    f"{biomarkers.get('fatigue_index', 0):.3f}",
                    f"{biomarkers.get('movement_smoothness', 0):.3f}",
                    result.get('performance_score', 0)
                ])
        
        output.seek(0)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name=f'screening_results_{timestamp}.csv'
        )
        
    except Exception as e:
        logger.error(f"Results download error: {e}")
        return jsonify({'success': False, 'error': str(e)})

# ==================== INITIALIZATION ====================

# Initialize components when app starts
logger.info("🚀 Military AI Screening System Starting...")
load_all_components()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🌐 Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
