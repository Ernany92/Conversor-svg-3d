import streamlit as st
import vtracer
import os
import cv2
import numpy as np
import base64
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# Configuração da página do Streamlit
st.set_page_config(page_title="Conversor SVG para Impressão 3D", page_icon="🖨️", layout="centered")

def otimizar_imagem_universal(imagem_pil, thresh_val, thickness):
    """Processa a imagem PIL diretamente na memória, isola o fundo e ajusta a espessura das linhas."""
    img = imagem_pil.convert("RGBA")
    w, h = img.size
    
    # Amostra os 4 cantos da imagem para detecção de fundo
    cantos = [img.getpixel((0, 0)), img.getpixel((w-1, 0)), img.getpixel((0, h-1)), img.getpixel((w-1, h-1))]
    
    luminosidades = []
    for c in cantos:
        if c[3] > 50:
            lum = 0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]
            luminosidades.append(lum)
    
    fundo_eh_escuro = len(luminosidades) > 0 and (sum(luminosidades) / len(luminosidades)) < 127
    
    if fundo_eh_escuro:
        base = Image.new("RGBA", img.size, (0, 0, 0, 255))
        base.paste(img, (0, 0), img)
        cinza = base.convert("L")
        imagem_final = ImageOps.invert(cinza)
    else:
        base = Image.new("RGBA", img.size, (255, 255, 255, 255))
        base.paste(img, (0, 0), img)
        imagem_final = base.convert("L")
    
    # Binarização utilizando o limiar (Threshold) dinâmico do controle deslizante
    imagem_binaria = imagem_final.point(lambda x: 0 if x < thresh_val else 255, 'L')
    
    # Convertemos para matriz OpenCV (NumPy) para aplicar a morfologia matemática (ajuste de espessura)
    img_np = np.array(imagem_binaria)
    
    if thickness > 0:
        kernel = np.ones((thickness, thickness), np.uint8)
        img_np = cv2.erode(img_np, kernel, iterations=1)
    elif thickness < 0:
        kernel = np.ones((abs(thickness), abs(thickness)), np.uint8)
        img_np = cv2.dilate(img_np, kernel, iterations=1)
    
    # Força caminho absoluto para salvar a imagem de transição limpa
    caminho_temp = os.path.abspath("temp_interface_processado.png")
    cv2.imwrite(caminho_temp, img_np)
    
    return caminho_temp, img_np

# --- INTERFACE GRÁFICA ---
st.title("🖨️ Conversor SVG Inteligente para Impressão 3D")
st.write("Transforme qualquer logotipo ou texto em um SVG limpo, sem blocos quadrados de fundo.")

# Componente de Upload de arquivo
arquivo_upload = st.file_uploader("Arraste ou seleciona uma imagem (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if arquivo_upload is not None:
    imagem_original = Image.open(arquivo_upload)
    
    # --- PAINEL LATERAL DE AJUSTES EM TEMPO REAL ---
    st.sidebar.header("🎛️ Controles do Traço")
    st.sidebar.markdown("Modifique os parâmetros abaixo até que o traço na prévia fique perfeito para o Bambu Studio.")
    
    thresh_val = st.sidebar.slider(
        "Definição das Bordas (Threshold)", 
        0, 255, 140,
        help="Ajusta o ponto de corte do contraste. Útil para eliminar sombras ou serrilhados do arquivo original."
    )
    
    thickness = st.sidebar.slider(
        "Grossura do Traço (Espessura)", 
        -15, 15, 0,
        help="Valores positivos engrossam linhas finas (evitando que sumam no fatiador). Valores negativos afinam traços muito unidos."
    )
    
    # Executa o processamento em tempo real (atualiza a cada movimento do slider)
    imagem_temporaria, img_preview = otimizar_imagem_universal(imagem_original, thresh_val, thickness)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sua Imagem")
        st.image(imagem_original, use_container_width=True)
        
    with col2:
        st.subheader("Prévia do Traço")
        
        # 🌟 LOGICA DA LUPA (CONVERSÃO BASE64 + HTML/JS INJETADO)
        _, buffer = cv2.imencode('.png', img_preview)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        
        html_zoom_component = f"""
        <div id="canvas-container" style="
            overflow: hidden; 
            width: 100%; 
            height: 380px; 
            border: 1px dashed #4A4A4A; 
            border-radius: 6px; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            background: #1A1A1A; 
            cursor: grab;
            user-select: none;
        ">
            <img id="bambu-preview" src="data:image/png;base64,{img_base64}" style="
                transform: translate(0px, 0px) scale(1); 
                transform-origin: center center; 
                transition: transform 0.05s ease-out; 
                max-width: 100%; 
                max-height: 100%; 
                object-fit: contain;
            " />
        </div>
        
        <script>
            const container = document.getElementById('canvas-container');
            const img = document.getElementById('bambu-preview');
            let scale = 1;
            let isDragging = false;
            let startX = 0, startY = 0;
            let translateX = 0, translateY = 0;

            // 1. Zoom Interativo por Rolagem do Mouse (Scroll Wheel)
            container.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const intensidadeZoom = 0.15;
                if (e.deltaY < 0) {{
                    scale += intensidadeZoom; // Zoom In
                }} else {{
                    scale -= intensidadeZoom; // Zoom Out
                }}
                scale = Math.min(Math.max(0.5, scale), 15); // Trava o zoom entre 0.5x e 15x
                img.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
            }}, {{ passive: false }});

            // 2. Sistema de Pan (Clique e arraste para navegar no desenho ampliado)
            container.addEventListener('mousedown', (e) => {{
                isDragging = true;
                container.style.cursor = 'grabbing';
                startX = e.clientX - translateX;
                startY = e.clientY - translateY;
            }});

            window.addEventListener('mouseup', () => {{
                isDragging = false;
                container.style.cursor = 'grab';
            }});

            container.addEventListener('mousemove', (e) => {{
                if (!isDragging) return;
                e.preventDefault();
                translateX = e.clientX - startX;
                translateY = e.clientY - startY;
                img.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
            }});
        </script>
        """
        # Renderiza a lousa interativa com altura controlada
        components.html(html_zoom_component, height=390)
        
        if st.button("🚀 Converter para SVG", use_container_width=True):
            with st.spinner("Vetorizando contornos..."):
                try:
                    # Define caminhos de saída absolutos
                    nome_original = os.path.splitext(arquivo_upload.name)[0]
                    caminho_svg_saida = os.path.abspath(f"{nome_original}_pronto_3d.svg")
                    
                    # Executa a vetorização do vtracer usando a imagem do preview ajustado
                    vtracer.convert_image_to_svg_py(
                        imagem_temporaria, 
                        caminho_svg_saida, 
                        colormode='binary',
                        mode='spline',       
                        filter_speckle=4,     
                        corner_threshold=60  
                    )
                    
                    # Lendo o arquivo gerado
                    with open(caminho_svg_saida, "rb") as f:
                        dados_svg = f.read()
                    
                    st.success("✅ SVG Gerado com Sucesso!")
                    
                    # Botão nativo de download
                    st.download_button(
                        label="📥 Baixar Arquivo SVG",
                        data=dados_svg,
                        file_name=os.path.basename(caminho_svg_saida),
                        mime="image/svg+xml",
                        use_container_width=True
                    )
                    
                    # Limpeza apenas do SVG local gerado
                    if os.path.exists(caminho_svg_saida):
                        os.remove(caminho_svg_saida)
                        
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
