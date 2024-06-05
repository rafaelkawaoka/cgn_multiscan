import fitz  # PyMuPDF
import os
import json
from datetime import datetime
import re

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    cpf_data_list = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        lines = text.split('\n')
        
        # Check the first seven lines for the specific text
        if any("COMPROVANTE DE INSCRIÇÃO CPF" in line for line in lines[:7]):
            cpf_data = {
                "tipo": "CPF",
                "numero": None,
                "nome": None,
                "nascimento": None
            }

            for i, line in enumerate(lines):
                if "Número" in line:
                    raw_number = lines[i + 1].strip() if i + 1 < len(lines) else None
                    if raw_number:
                        cpf_data["numero"] = re.sub(r'\D', '', raw_number)  # Remove all non-numeric characters
                elif "Nome" in line:
                    cpf_data["nome"] = lines[i + 1].strip() if i + 1 < len(lines) else None
                elif "Nascimento" in line:
                    raw_date = lines[i + 1].strip() if i + 1 < len(lines) else None
                    if raw_date:
                        try:
                            # Convert date from d/m/Y to Y-m-d
                            date_obj = datetime.strptime(raw_date, '%d/%m/%Y')
                            cpf_data["nascimento"] = date_obj.strftime('%Y-%m-%d')
                        except ValueError:
                            cpf_data["nascimento"] = None
            
            cpf_data_list.append(cpf_data)
            print(json.dumps(cpf_data, indent=4, ensure_ascii=False))
            print("\n" + "="*80 + "\n")

    return cpf_data_list

def process_all_pdfs_in_folder(folder_path):
    all_cpf_data = []
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, file_name)
            print(f"Processando arquivo: {file_name}")
            cpf_data_list = extract_text_from_pdf(pdf_path)
            all_cpf_data.extend(cpf_data_list)
    
    return all_cpf_data

# Exemplo de uso
if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    all_cpf_data = process_all_pdfs_in_folder(current_folder)
    # Save all CPF data to a JSON file if needed
    with open('cpf_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_cpf_data, f, ensure_ascii=False, indent=4)
