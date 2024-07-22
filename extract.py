import logging
import os
import subprocess
import tarfile

# Set up logging configuration
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO  # Adjust this to logging.DEBUG if you want more detailed logs
)

def extract_ova(ova_path, extract_path):
    logging.info('Starting extraction of OVA file: %s', ova_path)
    try:
        with tarfile.open(ova_path, 'r') as tar:
            tar.extractall(path=extract_path)
        logging.info('Extraction completed successfully.')
    except Exception as e:
        logging.error('Failed to extract OVA file: %s', e)
        raise

def convert_vmdk_to_qcow2(vmdk_path, qcow2_path):
    logging.info('Starting conversion of VMDK to QCOW2: %s', vmdk_path)
    try:
        subprocess.run(['qemu-img', 'convert', '-O', 'qcow2', vmdk_path, qcow2_path], check=True)
        logging.info('Conversion completed successfully.')
    except subprocess.CalledProcessError as e:
        logging.error('Failed to convert VMDK to QCOW2: %s', e)
        raise

def convert_ova_to_qcow2(ova_path, qcow2_output_path):
    logging.info('Starting conversion of OVA to QCOW2: %s', ova_path)
    extract_path = '/tmp/extracted_ova'
    os.makedirs(extract_path, exist_ok=True)

    try:
        extract_ova(ova_path, extract_path)

        for root, dirs, files in os.walk(extract_path):
            for file in files:
                if file.endswith('.vmdk'):
                    vmdk_path = os.path.join(root, file)
                    convert_vmdk_to_qcow2(vmdk_path, qcow2_output_path)
                    break
        logging.info('OVA to QCOW2 conversion completed successfully.')
    except Exception as e:
        logging.error('Failed during OVA to QCOW2 conversion: %s', e)
        raise
    finally:
        # Clean up extracted files
        try:
            subprocess.run(['rm', '-rf', extract_path], check=True)
            logging.info('Clean-up completed successfully.')
        except subprocess.CalledProcessError as e:
            logging.error('Failed to clean up extracted files: %s', e)

if __name__ == "__main__":
    # Example paths - replace with actual paths or modify as needed
    ova_path = 'path/to/your.ova'
    qcow2_output_path = 'path/to/your.qcow2'
    convert_ova_to_qcow2(ova_path, qcow2_output_path)
