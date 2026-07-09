import streamlit as st
import vtracer
import os
import cv2
import numpy as np
import base64
import re
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# Configuração da página do Streamlit
st.set_page_config(page_title="Conversor SVG para Impressão 3D", page_icon="🖨️", layout="centered")

def limpar_svg_para_fatiador(caminho_svg):
    """Abre o arquivo SVG gerado e remove cirurgicamente qualquer quadro ou linha de fundo."""
    if not os.path.exists(caminho_svg):
        return
        
    with open(caminho_svg, "r", encoding="utf-8") as f:
        conteudo = f.read()
    
    # 🌟 REMOÇÃO CIRÚRGICA: Deleta a tag <rect> (o quadro do canvas) e paths brancos de fundo
    # Isso garante que o fatiador veja APENAS as ilhas isoladas do logotipo preto.
    conteudo_limpo = re.sub(r'<rect[^>]*>', '', conteudo)
    conteudo_limpo = re.sub(r'<path[^>]*fill="#ffffff"[^>]*>', '', conteudo_limpo)
    conteudo_limpo = re.sub(r'<path[^>]*fill="white"[^>]*>', '', conteudo_limpo)
    conteudo_limpo = re.sub(r'<path[^>]*fill="#fff"[^>]*>', '', conteudo_limpo)
    
    with open(caminho_svg, "w", encoding="utf-8") as f:
        f.write(conteudo_limpo)

def otimizar_imagem_universal(imagem_pil, thresh_val, thickness):
    """Processa a imagem isolando o elemento em preto e limpando as extremidades."""
    img = imagem_pil.convert("RGBA")
    w, h = img.size
    
    # Amostra os 4 cantos da imagem para detecção inteligente de fundo
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
    
    # Binarização: O que você quer vira PRETO (0) e o resto vira BRANCO (255)
    imagem_binaria = imagem_final.point(lambda x: 0 if x < thresh_val else 255, 'L')
    img_np = np.array(imagem_binaria)
    
    # Ajuste de espessura morfológica baseada no traço preto
    if thickness > 0:
        kernel = np.ones((thickness, thickness), np.uint8)
        img_np = cv2.erode(img_np, kernel, iterations=1) # Engrossa o preto
    elif thickness < 0:
        kernel = np.ones((abs(thickness), abs(thickness)), np.uint8)
        img_np = cv2.dilate(img_np, kernel, iterations=1) # Afina o preto
    
    # Barreira extra de segurança nas bordas absolutas
    img_np[0:3, :] = 255
    img_np[-3:, :] = 255
    img_np[:, 0:3] = 255
    img_np[:, -3:] = 255
    
    caminho_temp = os.path.abspath("temp_interface_processado.png")
    cv2.imwrite(caminho_temp, img_np)
    
    return caminho_temp, img_np

# --- INTERFACE GRÁFICA ---
st.title("🖨️ Conversor SVG Inteligente para Impressão 3D")
st.write("Focado estritamente no seu desenho. Livre de molduras quadradas de fundo.")

arquivo_upload = st.file_uploader("Arraste ou selecione uma imagem (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if arquivo_upload is not None:
    imagem_original = Image.open(arquivo_upload)
    
    st.sidebar.header("🎛️ Controles do Traço")
    thresh_val = st.sidebar.slider("Definição das Bordas (Threshold)", 0, 255, 140)
    thickness = st.sidebar.slider("Grossura do Traço (Espessura)", -15, 15, 0)
    
    imagem_temporaria, img_preview = otimizar_imagem_universal(imagem_original, thresh_val, thickness)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sua Imagem")
        st.image(imagem_original, use_container_width=True)
        
    with col2:
        st.subheader("Prévia do Traço")
        st.caption("✨ Preto = O que será impresso | Branco = Totalmente ignorado")
        
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
            background: #F5F5F5; 
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

            container.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const intensidadeZoom = 0.15;
                if (e.deltaY < 0) {{
                    scale += intensidadeZoom;
                }} else {{
                    scale -= intensidadeZoom;
                }}
                scale = Math.min(Math.max(0.5, scale), 15);
                img.style.transform = `translate(${{translateX}}px, ${{translateY}}px) scale(${{scale}})`;
            }}, {{ passive: false }});

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
        components.html(html_zoom_component, height=390)
        
        if st.button("🚀 Converter para SVG", use_container_width=True):
            with st.spinner("Vetorizando e limpando arquivos de fundo..."):
                try:
                    nome_original = os.path.splitext(arquivo_upload.name)[0]
                    caminho_svg_saida = os.path.abspath(f"{nome_original}_pronto_3d.svg")
                    
                    # 1. Executa a vetorização nativa do VTracer
                    vtracer.convert_image_to_svg_py(
                        imagem_temporaria, 
                        caminho_svg_saida, 
                        colormode='binary',
                        mode='spline',       
                        hierarchical='cutout',
                        filter_speckle=4,     
                        corner_threshold=60  
                    )
                    
                    # 2. 🌟 ATUAÇÃO DIRETADA: Executa a faxina e deleta o quadro externo do código do SVG
                    limpar_svg_para_fatiador(caminho_svg_saida)
                    
                    with open(caminho_svg_saida, "rb") as f:
                        dados_svg = f.read()
                    
                    st.success("✅ SVG Limpo Gerado com Sucesso!")
                    
                    st.download_button(
                        label="📥 Baixar Arquivo SVG",
                        data=dados_svg,
                        file_name=os.path.basename(caminho_svg_saida),
                        mime="image/svg+xml",
                        use_container_width=True
                    )
                    
                    if os.path.exists(caminho_svg_saida):
                        os.remove(caminho_svg_saida)
                        
                except Exception as e:
                    st.error(f"Erro no processamento: {e}")
