import json
import os
import hashlib
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.core.window import Window

MASTER_PIN = "8899"
SECRET_SALT = "AutoScan_Pro_Cuba_2026_Key"

def obtener_id_dispositivo():
    try:
        from jnius import autoclass
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        Secure = autoclass('android.provider.Settings$Secure')
        content_resolver = PythonActivity.mActivity.getContentResolver()
        android_id = Secure.getString(content_resolver, Secure.ANDROID_ID)
        return android_id.upper()
    except Exception:
        return "DEV-PHONE-883912"

def calcular_clave_valida(device_id):
    cadena = f"{device_id}_{SECRET_SALT}"
    hash_obj = hashlib.sha256(cadena.encode('utf-8'))
    return hash_obj.hexdigest()[:8].upper()

def init_database():
    db_content = {
        "P0300": {
            "titulo": "Fallo de encendido en múltiples cilindros",
            "causa": "Bujías desgastadas, bobinas defectuosas o baja presión de gasolina.",
            "solucion": "Probar chispa en bobinas y medir presión en el riel de inyección."
        },
        "P0171": {
            "titulo": "Mezcla de aire/combustible demasiado pobre",
            "causa": "Sensor MAF sucio o entrada de aire no medida (fuga de vacío).",
            "solucion": "Limpiar sensor MAF con spray dieléctrico y revisar mangueras."
        }
    }
    if not os.path.exists("dtc_dict.json"):
        with open("dtc_dict.json", "w", encoding="utf-8") as f:
            json.dump(db_content, f, ensure_ascii=False, indent=2)

Window.clearcolor = (0.1, 0.12, 0.15, 1)

class AutoScanApp(App):
    def build(self):
        init_database()
        self.device_id = obtener_id_dispositivo()
        self.expected_key = calcular_clave_valida(self.device_id)
        
        if self.validar_licencia_guardada():
            return self.build_main_ui()
            
        return self.build_pin_ui()

    def validar_licencia_guardada(self):
        if os.path.exists("license.key"):
            try:
                with open("license.key", "r") as f:
                    saved_key = f.read().strip()
                return saved_key == self.expected_key
            except:
                return False
        return False

    def build_pin_ui(self):
        layout = BoxLayout(orientation='vertical', padding=25, spacing=15)
        
        layout.add_widget(Label(
            text="ACCESO RESTRINGIDO",
            font_size='22sp', bold=True, color=(1, 0.4, 0.4, 1), size_hint_y=0.15
        ))
        
        layout.add_widget(Label(
            text="Introduce el PIN Maestro para configurar e instalar la licencia en este dispositivo:",
            font_size='13sp', halign='center', size_hint_y=0.25
        ))
        
        self.pin_input = TextInput(
            hint_text="PIN Maestro", password=True, multiline=False,
            font_size='20sp', size_hint_y=0.2, background_color=(0.2, 0.2, 0.25, 1),
            foreground_color=(1, 1, 1, 1), input_filter='int'
        )
        layout.add_widget(self.pin_input)
        
        btn_pin = Button(
            text="VERIFICAR ADMIN", background_color=(0.1, 0.5, 0.8, 1),
            bold=True, size_hint_y=0.2
        )
        btn_pin.bind(on_press=self.verificar_pin)
        layout.add_widget(btn_pin)
        
        self.lbl_pin_status = Label(text="", font_size='12sp', size_hint_y=0.2, color=(1, 1, 0, 1))
        layout.add_widget(self.lbl_pin_status)
        
        return layout

    def verificar_pin(self, instance):
        if self.pin_input.text.strip() == MASTER_PIN:
            self.root.clear_widgets()
            self.root.add_widget(self.build_activation_ui())
        else:
            self.lbl_pin_status.text = "[!] PIN Maestro incorrecto. Acceso denegado."

    def build_activation_ui(self):
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        layout.add_widget(Label(
            text="REGISTRO DE DISPOSITIVO",
            font_size='20sp', bold=True, color=(0.2, 0.8, 1, 1), size_hint_y=0.1
        ))
        
        info = Label(
            text=f"CÓDIGO DE HARDWARE DE ESTE TELÉFONO:\n\n"
                 f"   >>>  {self.device_id}  <<<\n\n"
                 f"Introduce la Clave de Activación generada:",
            font_size='13sp', halign='center', size_hint_y=0.45
        )
        layout.add_widget(info)
        
        self.key_input = TextInput(
            hint_text="Clave de 8 dígitos", multiline=False, size_hint_y=0.15,
            font_size='16sp', background_color=(0.2, 0.2, 0.25, 1),
            foreground_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.key_input)
        
        btn_activate = Button(
            text="ACTIVAR Y BLOQUEAR A ESTE MÓVIL",
            background_color=(0, 0.7, 0.3, 1), bold=True, size_hint_y=0.15
        )
        btn_activate.bind(on_press=self.intentar_activacion)
        layout.add_widget(btn_activate)
        
        self.lbl_status = Label(text="", font_size='12sp', size_hint_y=0.15, color=(1, 1, 0, 1))
        layout.add_widget(self.lbl_status)
        
        return layout

    def intentar_activacion(self, instance):
        input_key = self.key_input.text.strip().upper()
        if input_key == self.expected_key:
            with open("license.key", "w") as f:
                f.write(input_key)
            self.root.clear_widgets()
            self.root.add_widget(self.build_main_ui())
        else:
            self.lbl_status.text = "[ERROR] Clave inválida para este hardware."

    def build_main_ui(self):
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        main_layout.add_widget(Label(
            text="AUTOSCAN PRO - LICENCIA ACTIVA",
            font_size='18sp', bold=True, size_hint_y=0.08, color=(0.2, 0.8, 1, 1)
        ))

        self.output_area = TextInput(
            text="[SISTEMA DESBLOQUEADO Y LISTO]\nPresiona 'ESCANEAR VEHÍCULO' para iniciar...\n",
            readonly=True, size_hint_y=0.70,
            background_color=(0.05, 0.07, 0.09, 1),
            foreground_color=(0.9, 0.9, 0.9, 1),
            font_size='12sp', multiline=True
        )
        main_layout.add_widget(self.output_area)

        btn_layout = BoxLayout(orientation='horizontal', spacing=8, size_hint_y=0.12)
        
        btn_scan = Button(text="ESCANEAR\nVEHÍCULO", background_color=(0, 0.6, 0.4, 1))
        btn_scan.bind(on_press=self.ejecutar_escaneo)
        
        btn_save = Button(text="GUARDAR\nREPORTE", background_color=(0.1, 0.5, 0.8, 1))
        btn_save.bind(on_press=self.guardar_reporte)

        btn_clear = Button(text="LIMPIAR", background_color=(0.7, 0.2, 0.2, 1))
        btn_clear.bind(on_press=self.limpiar_pantalla)
        
        btn_layout.add_widget(btn_scan)
        btn_layout.add_widget(btn_save)
        btn_layout.add_widget(btn_clear)
        main_layout.add_widget(btn_layout)

        btn_update = Button(
            text="ACTUALIZAR BASE DE DATOS (DTC)",
            background_color=(0.8, 0.5, 0, 1), bold=True, size_hint_y=0.10
        )
        btn_update.bind(on_press=self.actualizar_base_datos)
        main_layout.add_widget(btn_update)
        
        return main_layout

    def cargar_db(self):
        if os.path.exists("dtc_dict.json"):
            with open("dtc_dict.json", "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def actualizar_base_datos(self, instance):
        download_paths = [
            "/sdcard/Download/dtc_update.json",
            "dtc_update.json"
        ]
        updated = False
        for path in download_paths:
            if os.path.exists(path):
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        new_data = json.load(f)
                    db_current = self.cargar_db()
                    db_current.update(new_data)
                    with open("dtc_dict.json", "w", encoding="utf-8") as f:
                        json.dump(db_current, f, ensure_ascii=False, indent=2)
                    self.output_area.text = f"[ÉXITO] Base de datos actualizada con {len(new_data)} nuevos registros.\n"
                    updated = True
                    break
                except Exception as e:
                    self.output_area.text = f"[ERROR] Archivo dañado: {str(e)}\n"
                    return

        if not updated:
            self.output_area.text = (
                "[!] No se encontró 'dtc_update.json' en Descargas.\n"
                "1. Guarda el archivo enviado en la carpeta Descargas.\n"
                "2. Presiona este botón nuevamente."
            )

    def limpiar_pantalla(self, instance):
        self.output_area.text = "[SISTEMA LISTO]\n"

    def ejecutar_escaneo(self, instance):
        db = self.cargar_db()
        codes_detected = ["P0300", "P0171"]
        lines = [
            "==========================================",
            "      INFORME TÉCNICO DE DIAGNÓSTICO      ",
            "==========================================",
            "Vehículo: Geely Emgrand EC7 (2015)",
            "VIN: LB3711111F0000000",
            "------------------------------------------",
            f"Base de Datos Cargada: {len(db)} códigos activos\n"
        ]
        for code in codes_detected:
            info = db.get(code, {"titulo": "Falla desconocida", "causa": "N/A", "solucion": "N/A"})
            lines.append(f"• CÓDIGO: [{code}]")
            lines.append(f"  Diagnóstico: {info['titulo']}")
            lines.append(f"  Causa: {info['causa']}")
            lines.append(f"  Solución: {info['solucion']}\n")
        self.output_area.text = "\n".join(lines)

    def guardar_reporte(self, instance):
        file_path = "Reporte_Diagnostico.txt"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(self.output_area.text)
        self.output_area.text += f"\n\n[ÉXITO] Reporte guardado en el dispositivo."

if __name__ == '__main__':
    AutoScanApp().run()
