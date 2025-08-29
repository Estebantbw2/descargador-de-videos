import yt_dlp
import os 
import customtkinter as ctk # Importamos CustomTkinter
import threading # Necesario para ejecutar la descarga en segundo plano
from PIL import Image

import io # Necesario para manejar datos binarios como un archivo
import requests # N
import subprocess

import sys # para empaquetar ffmpeg

#https://www.gyan.dev/ffmpeg/builds/        FFMPEG          ffmpeg-release-essentials.zip

FFMPEG_PATH = "ffmpeg_bin"


directorio_base = os.path.expanduser("~")
descargas = os.path.join(directorio_base,"Downloads","tu pedido")

def descargarvainas(url, tipo="mp4", ubicacion=".",appi=None):


    global FFMPEG_PATH # Acceder a la variable global

    #crear carpeta
    os.makedirs(ubicacion , exist_ok=True)

    #configuraciones 

    ydl_opts = {
        'outtmpl': os.path.join(ubicacion, '%(title)s.%(ext)s'), # Plantilla para el nombre del archivo
        'noplaylist': True,                                        # Descarga solo el video individual, no listas
     #    'external_downloader': 'ffmpeg',                           # Usa FFmpeg para post-procesamiento/fusión
     #   'external_downloader_args': ['-loglevel', 'error'],        # Suprime mensajes detallados de FFmpeg
        'ffmpeg_location': FFMPEG_PATH,

    }
    if tipo == "mp4":
    # CAMBIO / ADICIÓN AQUÍ:
        # Pide a yt-dlp que prefiera video MP4 y audio M4A (que es AAC y más compatible).
        # Si no lo encuentra, retrocede a la mejor calidad general.
        ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'

        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]

    elif tipo == "mp3":
        ydl_opts['format'] = 'bestaudio/best'           # Descarga solo la mejor calidad de audio
        ydl_opts['extractaudio'] = True                 # Indica a yt-dlp que extraiga el audio
        ydl_opts['audioformat'] = 'mp3'                 # Formato de audio final
        ydl_opts['postprocessors'] = [{                 # Procesadores para convertir a MP3
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',                  # Calidad del MP3 en kbps

        }]
    elif tipo == "wav":
        ydl_opts['format'] = 'bestaudio/best'       # Descarga solo la mejor calidad de audio
        ydl_opts['extractaudio'] = True            # Indica a yt-dlp que extraiga el audio
        ydl_opts['audioformat'] = 'wav'            # Formato de audio final
        ydl_opts['postprocessors'] = [{            # Procesadores para convertir a WAV
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',

        }]
    elif tipo == "spotify_playlist":
        appi.estatus.configure(text=f"🎵 Descargando playlist de Spotify...",text_color="Gray")
        try:
            imagen_spotify = ctk.CTkImage(light_image=Image.open("spotify.png"), size=(100,100))
            appi.imagen = imagen_spotify
            appi.imagen_label.configure(image=imagen_spotify)
        except Exception as e:
            appi.imagen_label.configure(image=None)
            appi.imagen = None
        try:
            comando = [
                "spotdl",
                "download",
                url,
                "--output", os.path.join(ubicacion, "{artist} - {title}.{ext}"),
                "--lyrics", "genius"  # Usa Genius para letras, evita azlyrics
            ]
            resultado = subprocess.run(comando, capture_output=True, text=True, encoding="utf-8")
            print("spotdl stdout:", resultado.stdout)
            print("spotdl stderr:", resultado.stderr)
            if resultado.returncode == 0:
                appi.estatus.configure(text=f"✅ Playlist descargada con spotdl ✅\n{resultado.stdout}",text_color="Green")
            else:
                appi.estatus.configure(text=f"❌ Error con spotdl ❌\n{resultado.stderr}",text_color="Red")
        except Exception as e:
            print(f"❌ Ocurrió un error con spotdl: {e}")
            appi.estatus.configure(text=f"❌ERROR con spotdl❌\n{e}",text_color="Red")
        return
    else:
        print("⚠️ Tipo de medio no válido. Descargando como MP4 por defecto.")
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
        ydl_opts['merge_output_format'] = 'mp4'

        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
            
        }]


    #descargar 

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            # Obtiene información del video sin descargarlo para mostrar el título

            info = ydl.extract_info(url, download=False)

            title = info.get('title', 'Video Desconocido') # Usa 'Video Desconocido' si no se encuentra el título

            foto = info.get('thumbnail')
            datos_foto= appi.descargarImagen(foto)
            
            imagen_foto = io.BytesIO(datos_foto)
            
            appi.imagen=ctk.CTkImage(light_image=Image.open(imagen_foto),size=(100,100))
            appi.imagen_label.configure(image=appi.imagen)


       

            appi.estatus.configure(text=f"🎬 Descargando '{title}' como {tipo.upper()}...",text_color="Gray")
      

            print(f"🎬 Descargando '{title}' como {tipo.upper()}...")

            ydl.download([url]) # Inicia la descarga

        print(f"✅ Descarga completada para: {title}")

        app.estatus.configure(text="✅Descargado✅!!! epa",text_color="Green")


    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")
        print("Consejo: Asegúrate de que FFmpeg esté instalado y su directorio 'bin' esté en tu PATH.")
        app.estatus.configure(text="❌ERROR, PONGA EL LINK PUES! Escriba bien❌",text_color="Red")

if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # Estamos en un ejecutable de PyInstaller
    base_path = sys._MEIPASS
    # Construye la ruta al ejecutable de FFmpeg dentro de la carpeta temporal
    # Asume que ffmpeg.exe (o ffmpeg para Linux/macOS) está en la raíz de ffmpeg_bin
    FFMPEG_PATH = os.path.join(base_path, 'ffmpeg_bin', 'ffmpeg.exe') # Ajusta para Linux/macOS si es necesario
    # O para ser más general, podrías solo apuntar a la carpeta si sabes que ffmpeg.exe está dentro:
    # FFMPEG_PATH = os.path.join(base_path, 'ffmpeg_bin')
else:
    # No estamos en un ejecutable, ejecutando desde el script .py
    # Asume que ffmpeg.exe está en el PATH o en la carpeta ffmpeg_bin
    FFMPEG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ffmpeg_bin', 'ffmpeg.exe')
    # Si quieres que aún use el PATH si no está en ffmpeg_bin:
    # FFMPEG_PATH = "ffmpeg" # Deja que yt-dlp lo busque en PATH

class Aplicacion(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Descargador legal")
        self.geometry("600x400")
        self.minsize(600, 400)

        self.titulo =ctk.CTkLabel(master=self, text="Descargador de videos 100'%'seguro",font=("Impact",30),text_color="Red")
        self.titulo.place(relx=0.5,rely=0.08,anchor="n")
        
        self.entrada=ctk.CTkEntry(self, height=50, placeholder_text="URL acá")
        self.entrada.place(relx=0.4,rely=0.2,relwidth=0.6,relheight=0.15, anchor="n")

        self.entrada2=ctk.CTkEntry(self, height=45, placeholder_text="Nombre de carpeta de descarga. Si no pone nada va pa descargas")
        self.entrada2.place(relx=0.4,rely=0.35,relwidth=0.6,relheight=0.15, anchor="n")


        self.opciones=ctk.CTkComboBox(self, height=50,values=["mp4","mp3","wav","spotify_playlist"])
        self.opciones.place(relx=0.8,rely=0.2,relwidth=0.2,relheight=0.15, anchor="n")

        self.boton=ctk.CTkButton(self,corner_radius=50, text="VRAMOS!!!",command=self.tocoBoton)
        self.boton.place(relx=0.8,rely=0.35,relwidth=0.2,relheight=0.15, anchor="n")

        self.imagen_label=ctk.CTkLabel(self,text="" )
        self.imagen_label.place(relx=0.5,rely=0.55,relwidth=0.3,relheight=0.3,anchor="n")

        
        self.imagen_label.bind("<Configure>", self.tamanoImagen)


        self.estatus =ctk.CTkLabel(master=self,font=("Impact",20), text="")
        self.estatus.place(relx=0.5,rely=0.9,anchor="n")

        self.imagen = None  # Inicializa la imagen


    def tocoBoton(self):
        url = self.entrada.get()
        opcion = self.opciones.get()
        if opcion == "spotify_playlist" and "spotify.com/playlist" not in url:
            self.estatus.configure(text="❌ Debe ingresar un enlace de playlist de Spotify ❌",text_color="Red")
            return
        la_ubicacion=self.entrada2.get()

        if la_ubicacion != "".lower():
            ubicacion= la_ubicacion
        else:
            ubicacion = descargas
            print(ubicacion)
        

        self.boton.configure(state="disabled")
        self.entrada.configure(state="disabled")
        self.entrada2.configure(state="disabled")
        self.opciones.configure(state="disabled")          
        self.estatus.configure(text="...Descargando..." ,text_color="Gray")
        self.imagen_label.configure(image=None)

        print(url,opcion,la_ubicacion)
        #importante!!!
        download_thread = threading.Thread(target=descargarvainas, args=(url, opcion, ubicacion,self))
        download_thread.start()
        
        # Iniciar el monitoreo del hilo para re-habilitar la GUI cuando termine
        self.after(100, self.revisarDescarga, download_thread)


    def descargarImagen(self,imagen_url):
        print("descargando imagen")
        response = requests.get(imagen_url, stream=True)
        response.raise_for_status()
        return response.content

    def tamanoImagen(self, event):
        label_width = self.imagen_label.winfo_width()
        label_height = self.imagen_label.winfo_height()
        if self.imagen is not None:
            self.imagen.configure(size=(label_width, label_height))
        print(event)

    
    def revisarDescarga(self, thread):
        """
        Monitorea el hilo de descarga. Si ha terminado, re-habilita los controles de la GUI.
        """
        if thread.is_alive():
            # Si el hilo sigue vivo, vuelve a verificar en 100ms
            self.after(100, self.revisarDescarga, thread)
        else:
            # El hilo ha terminado, re-habilitar la GUI
            self.boton.configure(state="normal")
            self.entrada.configure(state="normal")
            self.entrada2.configure(state="normal")
            self.opciones.configure(state="normal")
       

            # El estado final ya lo actualizó descargarvainas
            print("Hilo de descarga finalizado.")



if __name__== "__main__":
    
    app = Aplicacion()
    app.mainloop()
