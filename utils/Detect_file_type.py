import os 
import magic

def detect_file_type() : 
    tesintg_file = "./certificat_medical.pdf"
    if not os.path.exists(tesintg_file) : 
        print("error file not found")
    else : 
        file_type = magic.from_file(tesintg_file )
        print(f"file type : {file_type}")
        if "PDF document" in file_type : 
            print("nice")


def detect_from_byte() : 
    tesintg_file = "./certificat_medical.pdf"
    with open(tesintg_file , "rb") as f : 
        data = f.read(2048)
    print(magic.from_buffer(data))

detect_from_byte()
