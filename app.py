import streamlit as st
import fitz  # PyMuPDF
from PIL import Image
import os
import shutil # Importamos shutil para manejar la eliminación de carpetas

def pdf_a_jpg_streamlit():
    """
    Convierte un PDF a imágenes JPG numeradas para una aplicación Streamlit.
    Permite al usuario subir un PDF y especificar una carpeta de salida.
    """
    st.set_page_config(
        page_title="PDF a JPG Converter",
        page_icon="📄",
        layout="centered"
    )

    st.title("📄 Conversor de PDF a JPG")
    st.markdown("Sube tu archivo PDF y lo convertiremos a imágenes JPG, una por página.")

    # 1. Cargar el archivo PDF
    pdf_file = st.file_uploader("Sube un archivo PDF aquí", type=["pdf"])

    if pdf_file is not None:
        # Mostrar el nombre del archivo subido
        st.write(f"Archivo PDF cargado: **{pdf_file.name}**")

        # 2. Definir la carpeta de salida
        # Usamos st.session_state para mantener el valor entre re-ejecuciones
        if "output_folder_name" not in st.session_state:
            st.session_state.output_folder_name = "pdf_jpg_salida"

        output_folder_input = st.text_input(
            "Nombre de la carpeta donde guardar las imágenes (dejar vacío para 'pdf_jpg_salida'):",
            value=st.session_state.output_folder_name
        )

        if output_folder_input:
            st.session_state.output_folder_name = output_folder_input
        else:
            st.session_state.output_folder_name = "pdf_jpg_salida"
        
        salida_carpeta = st.session_state.output_folder_name

        # Botón para iniciar la conversión
        if st.button("✨ Iniciar Conversión"):
            # Crear una carpeta temporal para el PDF subido y los JPGs
            temp_dir = "temp_pdf_to_jpg"
            os.makedirs(temp_dir, exist_ok=True)
            pdf_path_temp = os.path.join(temp_dir, pdf_file.name)

            # Guardar el PDF subido temporalmente
            with open(pdf_path_temp, "wb") as f:
                f.write(pdf_file.getbuffer())

            # Crear la carpeta de salida dentro del directorio temporal para Streamlit Cloud
            output_path_full = os.path.join(temp_dir, salida_carpeta)
            os.makedirs(output_path_full, exist_ok=True)

            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                pdf_document = fitz.open(pdf_path_temp)
                total_paginas = len(pdf_document)
                st.info(f"📄 PDF cargado: **{pdf_file.name}** ({total_paginas} páginas)")

                for pagina_num in range(total_paginas):
                    pagina = pdf_document.load_page(pagina_num)
                    # Ajusta el DPI para mejor calidad si es necesario, 200 es un buen balance
                    pix = pagina.get_pixmap(dpi=200)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    
                    jpg_filename = f"{pagina_num + 1}.jpg"
                    img_save_path = os.path.join(output_path_full, jpg_filename)
                    img.save(img_save_path, quality=95)
                    
                    progress_value = (pagina_num + 1) / total_paginas
                    progress_bar.progress(progress_value)
                    status_text.text(f"Convertiendo página {pagina_num + 1}/{total_paginas}...")

                st.success(f"✅ ¡Conversión completada! Se generaron {total_paginas} imágenes JPG.")
                st.write(f"Puedes ver las imágenes convertidas en la barra lateral o descargarlas más abajo.")

                # Mostrar las imágenes en la barra lateral para visualización
                st.sidebar.header("Imágenes Convertidas")
                for i in range(total_paginas):
                    img_name = f"{i + 1}.jpg"
                    img_path = os.path.join(output_path_full, img_name)
                    st.sidebar.image(img_path, caption=f"Página {i+1}", use_column_width=True)
                
                # Crear un archivo ZIP para descargar todas las imágenes
                zip_filename = f"{os.path.splitext(pdf_file.name)[0]}_imagenes.zip"
                zip_path = os.path.join(temp_dir, zip_filename)
                
                shutil.make_archive(os.path.splitext(zip_path)[0], 'zip', output_path_full)
                
                with open(zip_path, "rb") as fp:
                    btn = st.download_button(
                        label="⬇️ Descargar todas las imágenes (ZIP)",
                        data=fp,
                        file_name=zip_filename,
                        mime="application/zip"
                    )

            except Exception as e:
                st.error(f"❌ Error durante la conversión: {e}")
            finally:
                if 'pdf_document' in locals() and pdf_document:
                    pdf_document.close()
                
                # Limpiar el directorio temporal después de la operación
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)
                    st.info("Archivos temporales eliminados.")

# Punto de entrada para la aplicación Streamlit
if __name__ == "__main__":
    pdf_a_jpg_streamlit()