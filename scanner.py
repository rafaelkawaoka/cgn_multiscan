import fitz  # PyMuPDF
import os
import json
from datetime import datetime
import re
import shutil

def create_directory(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def format_filename(name):
    return name.lower().replace(" ", "_")

def extract_text_from_pdf(pdf_path):
    document_data_list = []
    all_text = ""
    move_file = False
    move_destination = None

    with fitz.open(pdf_path) as doc:
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text("text")
            all_text += f"Conteúdo da página {page_num + 1} do arquivo {pdf_path}:\n{text}\n\n"
            lines = text.split('\n')

            # Check the first seven lines for CPF
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
                
                document_data_list.append(cpf_data)
                print(json.dumps(cpf_data, indent=4, ensure_ascii=False))
                print("\n" + "="*80 + "\n")

                # Prepare to move the CPF document to the "CPF" folder
                if cpf_data["nome"]:
                    cpf_folder = os.path.join(os.getcwd(), "CPF")
                    create_directory(cpf_folder)
                    formatted_name = format_filename(cpf_data["nome"])
                    move_destination = os.path.join(cpf_folder, f"{formatted_name}_cpf.pdf")
                    move_file = True

            # Check the first ten lines for "Formulario e-consular"
            elif all("e-consular" in line or "Dados do requerimento" in line for line in lines[:10]):
                form_data = {
                    "tipo": "Formulario e-consular",
                    "nome": None,
                    "cpf": None,
                    "email": None,
                    "telefone": None
                }

                for i, line in enumerate(lines):
                    if "Dados do usuário" in line:
                        for j in range(i + 1, len(lines)):
                            if "Nome" in lines[j]:
                                form_data["nome"] = lines[j + 1].strip() if j + 1 < len(lines) else None
                            elif "CPF" in lines[j]:
                                raw_cpf = lines[j + 1].strip() if j + 1 < len(lines) else None
                                if raw_cpf:
                                    form_data["cpf"] = re.sub(r'\D', '', raw_cpf)  # Remove all non-numeric characters
                            elif "Email" in lines[j]:
                                form_data["email"] = lines[j + 1].strip() if j + 1 < len(lines) else None
                            elif "Telefone" in lines[j]:
                                form_data["telefone"] = lines[j + 1].strip() if j + 1 < len(lines) else None
                            if all(form_data.values()):
                                break
                
                document_data_list.append(form_data)
                print(json.dumps(form_data, indent=4, ensure_ascii=False))
                print("\n" + "="*80 + "\n")

    return document_data_list, all_text, move_file, move_destination

def process_all_pdfs_in_folder(folder_path):
    all_document_data = []
    all_text = ""
    for file_name in os.listdir(folder_path):
        pdf_path = os.path.join(folder_path, file_name)
        if file_name.endswith('.pdf') and os.path.isfile(pdf_path):
            print(f"Processando arquivo: {file_name}")
            document_data_list, text, move_file, move_destination = extract_text_from_pdf(pdf_path)
            all_document_data.extend(document_data_list)
            all_text += text
            if move_file and move_destination:
                shutil.move(pdf_path, move_destination)
    
    return all_document_data, all_text

# Exemplo de uso
if __name__ == "__main__":
    current_folder = os.path.dirname(os.path.abspath(__file__))
    all_document_data, all_text = process_all_pdfs_in_folder(current_folder)
    
    # Save all document data to a JSON file
    with open('document_data.json', 'w', encoding='utf-8') as f:
        json.dump(all_document_data, f, ensure_ascii=False, indent=4)

    # Save all text content to docs.txt
    with open('docs.txt', 'w', encoding='utf-8') as f:
        f.write(all_text)
