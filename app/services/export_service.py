import os
import pandas as pd
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fpdf import FPDF
from app.models.property import Property

class ExportService:
    EXPORT_DIR = "/tmp/exports"
    
    @classmethod
    def _ensure_dir(cls):
        if not os.path.exists(cls.EXPORT_DIR):
            os.makedirs(cls.EXPORT_DIR)

    @classmethod
    async def export_properties_excel(cls, properties: List[Property], filename: str = "properties.xlsx") -> str:
        """Evlərin siyahısını Excel (xlsx) formatında generasiya edir və faylın yolunu qaytarır."""
        cls._ensure_dir()
        file_path = os.path.join(cls.EXPORT_DIR, filename)
        
        data = []
        for p in properties:
            data.append({
                "ID": p.id,
                "Başlıq": p.title,
                "Qiymət (AZN)": p.price,
                "Sahə (kv.m)": p.area,
                "Otaq Sayı": p.room_count,
                "Rayon": p.district,
                "Ünvan": p.address,
                "Status": p.status.value,
                "Əlavə Edilmə Tarixi": p.created_at.strftime("%Y-%m-%d %H:%M")
            })
            
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, engine='openpyxl')
        return file_path

    @classmethod
    async def export_properties_pdf(cls, properties: List[Property], filename: str = "properties.pdf") -> str:
        """Evlərin siyahısını sadə cədvəl formasında PDF-ə çıxarır."""
        cls._ensure_dir()
        file_path = os.path.join(cls.EXPORT_DIR, filename)
        
        pdf = FPDF()
        pdf.add_page()
        # Məhdud mühitdə standart fontlar istifadə olunur (Unicode məhdudiyyətləri ola bilər, productionda custom TTF əlavə olunur)
        pdf.set_font("Helvetica", size=12)
        
        pdf.cell(200, 10, txt="NEXORA CRM - Evlerin Hesabati", ln=1, align='C')
        pdf.ln(10)
        
        # Table Header
        pdf.set_font("Helvetica", style="B", size=10)
        pdf.cell(15, 10, "ID", 1)
        pdf.cell(50, 10, "Basliq (Qisa)", 1)
        pdf.cell(30, 10, "Qiymet", 1)
        pdf.cell(30, 10, "Rayon", 1)
        pdf.cell(30, 10, "Status", 1)
        pdf.ln()
        
        # Table Body
        pdf.set_font("Helvetica", size=9)
        for p in properties:
            # Uzun başlıqları kəsirik
            short_title = p.title[:20] + ".." if len(p.title) > 20 else p.title
            # Sadə ASCII xarakterlərə çeviririk ki PDF standart fontda xəta verməsin
            safe_title = short_title.encode('ascii', 'ignore').decode('ascii')
            safe_district = p.district.encode('ascii', 'ignore').decode('ascii')
            
            pdf.cell(15, 10, str(p.id), 1)
            pdf.cell(50, 10, safe_title, 1)
            pdf.cell(30, 10, str(p.price), 1)
            pdf.cell(30, 10, safe_district, 1)
            pdf.cell(30, 10, p.status.value, 1)
            pdf.ln()
            
        pdf.output(file_path)
        return file_path
