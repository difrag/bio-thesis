import streamlit as st
import pandas as pd
from PIL import Image
import subprocess
import os
import base64
import pickle
from pathlib import Path
#from joblib import load
import numpy as np

# Molecular descriptor calculator - Improved version
def desc_calc():
    try:
        import subprocess
        from pathlib import Path
        import os
        
        # 1. Get ABSOLUTE paths (critical for Windows)
        current_dir = Path(__file__).parent.absolute()
        padel_dir = current_dir / "PaDEL-Descriptor"
        jar_path = padel_dir / "PaDEL-Descriptor.jar"
        xml_path = padel_dir / "PubchemFingerprinter.xml"
        
        # 2. Verify ALL files exist (with debug output)
        st.write("🔍 Checking paths...")
        st.write(f"Project directory: {current_dir}")
        st.write(f"JAR exists: {jar_path.exists()} at {jar_path}")
        st.write(f"XML exists: {xml_path.exists()} at {xml_path}")
        
        if not jar_path.exists():
            raise FileNotFoundError(f"PaDEL-Descriptor.jar missing at {jar_path}")
        if not xml_path.exists():
            raise FileNotFoundError(f"PubchemFingerprinter.xml missing at {xml_path}")

        # 3. Find Java (try multiple methods)
        java_path = None
        # Method 1: Check JAVA_HOME
        if "JAVA_HOME" in os.environ:
            java_path = Path(os.environ["JAVA_HOME"]) / "bin" / "java.exe"
            if not java_path.exists():
                java_path = None
                
        # Method 2: Check system PATH
        if java_path is None:
            try:
                subprocess.run(["java", "-version"], check=True, capture_output=True)
                java_path = "java"  # Use system java
            except:
                pass
                
        if java_path is None:
            raise RuntimeError("Java not found! Install from https://adoptium.net/")

        # 4. Prepare command with explicit paths
        cmd = [
            str(java_path),
            "-Xms2G",
            "-Xmx2G",
            "-Djava.awt.headless=true",
            "-jar", str(jar_path),
            "-removesalt",
            "-standardizenitro",
            "-fingerprints",
            "-descriptortypes", str(xml_path),
            "-dir", str(current_dir),
            "-file", "descriptors_output.csv"
        ]
        
        st.write("⚙️ Command:", " ".join(cmd))
        
        # 5. Run with explicit working directory
        result = subprocess.run(
            cmd,
            cwd=str(current_dir),  # CRITICAL for Windows
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True  # Needed for Windows path resolution
        )
        
        if result.returncode != 0:
            error_msg = result.stderr or "Unknown error"
            if "java.lang" in error_msg:
                error_msg += "\n\n⚠️ Java version mismatch? Try Java 8 or 11"
            raise RuntimeError(f"PaDEL failed:\n{error_msg}")
            
        st.success("Descriptors calculated successfully!")
        
    except Exception as e:
        st.error(f"""
        🚨 CRITICAL ERROR
        
        {str(e)}
        
        🔧 TROUBLESHOOTING:
        1. Verify Java 8 or 11 is installed (current: {'java -version'})
        2. Check ALL these files exist:
           - {jar_path}
           - {xml_path}
        3. Try moving project to shorter path (e.g. E:\bio_app)
        4. Ensure no special characters (!@#) in path
        """)
        st.stop()

# File download (unchanged)
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="prediction.csv">Download Predictions</a>'
    return href

# Model building with error handling
def build_model(input_data):
    try:
        model_path = Path('amyloid_model.pkl')
        if not model_path.exists():
            raise FileNotFoundError("Model file not found")
            
        with open(model_path, 'rb') as f:
            load_model = pickle.load(f)
            
        prediction = load_model.predict(input_data)
        st.header('**Prediction output**')
        prediction_output = pd.Series(prediction, name='pIC50')
        molecule_name = pd.Series(load_data[1], name='molecule_name')
        df = pd.concat([molecule_name, prediction_output], axis=1)
        st.write(df)
        st.markdown(filedownload(df), unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Model prediction failed: {str(e)}")
        st.stop()

# Logo image with existence check
try:
    image = Image.open('logo.png')
    st.image(image, use_column_width=True)
except FileNotFoundError:
    st.warning("Logo image not found, continuing without it")

# Page title
st.markdown("""
# Bioactivity Prediction App (Acetylcholinesterase)

This app predicts bioactivity towards inhibiting the `Acetylcholinesterase` enzyme, a drug target for Alzheimer's disease.

**Credits**
- App built in `Python` + `Streamlit` by [Chanin Nantasenamat](https://medium.com/@chanin.nantasenamat)
- Descriptor calculated using [PaDEL-Descriptor](http://www.yapcwsoft.com/dd/padeldescriptor/)
---
""")

# Sidebar
with st.sidebar.header('1. Upload your CSV data'):
    uploaded_file = st.sidebar.file_uploader("Upload your input file", type=['txt'])
    st.sidebar.markdown("""
[Example input file](https://raw.githubusercontent.com/dataprofessor/bioactivity-prediction-app/main/example_acetylcholinesterase.txt)
""")

if st.sidebar.button('Predict'):
    if uploaded_file is None:
        st.error("Please upload an input file first")
        st.stop()
        
    try:
        load_data = pd.read_table(uploaded_file, sep=' ', header=None)
        load_data.to_csv('molecule.smi', sep='\t', header=False, index=False)

        st.header('**Original input data**')
        st.write(load_data)

        with st.spinner("Calculating descriptors..."):
            desc_calc()

        # Read descriptors with error handling
        try:
            desc = pd.read_csv('descriptors_output.csv')
            st.header('**Calculated molecular descriptors**')
            st.write(desc)
            st.write(desc.shape)

            # Read descriptor list
            descriptor_list = Path('descriptor_list.csv')
            if not descriptor_list.exists():
                raise FileNotFoundError("Descriptor list file not found")
                
            Xlist = list(pd.read_csv(descriptor_list).columns)
            desc_subset = desc[Xlist]
            
            st.header('**Subset of descriptors from previously built models**')
            st.write(desc_subset)
            st.write(desc_subset.shape)

            build_model(desc_subset)
            
        except Exception as e:
            st.error(f"Error processing descriptors: {str(e)}")
            st.stop()
            
    except Exception as e:
        st.error(f"Error processing input file: {str(e)}")
        st.stop()
else:
    st.info('Upload input data in the sidebar to start!')