import sys
import gi
import subprocess
import keyring
import minecraft_launcher_lib
import configparser
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, Gdk, Graphene, GLib

# Azure application
CLIENT_ID = "FILLME"
REDIRECT_URL = "http://localhost"
TITLE = "Kreato Launcher"

minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
config = configparser.RawConfigParser()

def set_status(status: str):
    print(status)


def set_progress(progress: int):
    if current_max != 0:
        print(f"{progress}/{current_max}")


def set_max(new_max: int):
    global current_max
    current_max = new_max




class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.set_default_size(300, 250)
        self.set_title(TITLE)

        # Main layout containers
        self.box1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.box2 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.box3 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        self.box2.set_spacing(10)
        self.box2.set_margin_top(10)
        self.box2.set_margin_bottom(10)
        self.box2.set_margin_start(10)
        self.box2.set_margin_end(10)

        self.set_child(self.box1)  # Horizontal box to window
        self.box1.append(self.box2)  # Put vert box in that box
        self.box1.append(self.box3)  # And another one, empty for now

        # Add a button
        self.button = Gtk.Button(label="Launch")
        self.button.connect('clicked', self.launch_mc)
        self.box2.append(self.button)  # But button in the first of the two vertical boxes
        self.button = Gtk.Button(label="Install")
        self.button.connect('clicked', self.install_mc)
        self.box2.append(self.button)  # But button in the first of the two vertical boxes

        self.button = Gtk.Button(label="Install Fabric")
        self.button.connect('clicked', self.install_fabric)
        self.box2.append(self.button)  # But button in the first of the two vertical boxes


        # Add a check button
        self.check = Gtk.CheckButton(label="Don't close launcher when Minecraft launches")
        self.box2.append(self.check)

        # Add a box containing a switch and label
        self.switch_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.switch_box.set_spacing(5)

        self.switch = Gtk.Switch()
        self.switch.set_active(True)  # Let's default it to on
        self.switch.connect("state-set", self.switch_switched)  # Lets trigger a function on state change

        name_store = Gtk.ListStore(int, str)

        mine = minecraft_launcher_lib.utils.get_available_versions(minecraft_directory)

        for x in range(0, len(mine)):
            name_store.append([x, mine[x]["id"]])

        self.combox = Gtk.ComboBox.new_with_model_and_entry(name_store)
        self.combox.connect("changed", self.on_name_combo_changed)
        self.combox.set_entry_text_column(1)
        self.combox.set_active(0)
        self.box2.append(self.combox)
        
        #self.label = Gtk.Label(label="A switch")

        #self.switch_box.append(self.switch)
        #self.switch_box.append(self.label)
        #self.box2.append(self.switch_box)

        #self.slider = Gtk.Scale()
        #self.slider.set_digits(0)  # Number of decimal places to use
        #self.slider.set_range(0, 10)
        #self.slider.set_value(5)  # Sets the current value/position
        #self.slider.connect('value-changed', self.slider_changed)
        #self.box2.append(self.slider)

        self.header = Gtk.HeaderBar()
        self.set_titlebar(self.header)
    
        #self.open_button = Gtk.Button(label="Open")
        #self.header.pack_start(self.open_button)
        #self.open_button.set_icon_name("document-open-symbolic")

        #self.open_dialog = Gtk.FileChooserNative.new(title="Choose a file", parent=self, action=Gtk.FileChooserAction.OPEN)

        #self.open_dialog.connect("response", self.open_response)
        #self.open_button.connect("clicked", self.show_open_dialog)

        #f = Gtk.FileFilter()
        #f.set_name("Image files")
        #f.add_mime_type("image/jpeg")
        #f.add_mime_type("image/png")
        #self.open_dialog.add_filter(f)


        # Create a new "Action"
        action = Gio.SimpleAction.new("login", None)
        action.connect("activate", self.login)
        self.add_action(action)  # Here the action is being added to the window, but you could add it to the
        # application or an "ActionGroup"

        # Create a new menu, containing that action
        menu = Gio.Menu.new()
        menu.append("Login", "win.login")  # Or you would do app.grape if you had attached the
        
        # Create a popover
        self.popover = Gtk.PopoverMenu()  # Create a new popover menu
        self.popover.set_menu_model(menu)

        # Create a menu button
        self.hamburger = Gtk.MenuButton()
        self.hamburger.set_popover(self.popover)
        self.hamburger.set_icon_name("open-menu-symbolic")  # Give it a nice icon

        # Add menu button to the header bar
        self.header.pack_start(self.hamburger)

        # set app name
        GLib.set_application_name(TITLE)

        # Add an about dialog
        action = Gio.SimpleAction.new("about", None)
        action.connect("activate", self.show_about)
        self.add_action(action)  # Here the action is being added to the window, but you could add it to the
        menu.append("About", "win.about")

        app = self.get_application()
        sm = app.get_style_manager()
        sm.set_color_scheme(Adw.ColorScheme.PREFER_DARK)

    def on_name_combo_changed(self, combox):
        global mc_ver
        tree_iter = combox.get_active_iter()
        if tree_iter is not None:
            model = combox.get_model()
            row_id, name = model[tree_iter][:2]
            #print("Selected: ID=%d, name=%s" % (row_id, name))
            mc_ver = name
        else:
            entry = combox.get_child()
            #print("Entered: %s" % entry.get_text())
            mc_ver = entry.get_text()

    def show_about(self, action, param):
        self.about = Gtk.AboutDialog()
        self.about.set_transient_for(self)
        self.about.set_modal(self)

        self.about.set_authors(["Kreato"])
        self.about.set_copyright("Copyright 2022 Kreato")
        self.about.set_license_type(Gtk.License.GPL_3_0)
        self.about.set_website("https://kreato.dev")
        self.about.set_website_label("kreato.dev")
        self.about.set_version("1.0")
        self.about.set_logo_icon_name("org.kreato.launcher")

        self.about.show()

    def key_press(self, event, keyval, keycode, state):
        if keyval == Gdk.KEY_q and state & Gdk.ModifierType.CONTROL_MASK:
            self.close()

    def show_open_dialog(self, button):
        self.open_dialog.show()

    def open_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file = dialog.get_file()
            filename = file.get_path()
            print(filename)

    def login(self, action, param):
        global options
        login_url, state, code_verifier = minecraft_launcher_lib.microsoft_account.get_secure_login_data(CLIENT_ID, REDIRECT_URL)
        print(f"Please open {login_url} in your browser and copy the url you are redirected into the prompt below.")
        code_url = input()
        # Get the code from the url
        try:
            auth_code = minecraft_launcher_lib.microsoft_account.parse_auth_code_url(code_url, state)
        except AssertionError:
            print("States do not match!")
            sys.exit(1)
        except KeyError:
            print("Url not valid")
            sys.exit(1)

        # Get the login data
        login_data = minecraft_launcher_lib.microsoft_account.complete_login(CLIENT_ID, None, REDIRECT_URL, auth_code, code_verifier)

        # Get Minecraft command
        options = {
            "username": login_data["name"],
            "uuid": login_data["id"],
            "token": login_data["access_token"]
        }
        
        config.add_section("UserInfo")
        config.set("UserInfo", "username", login_data["name"])
        config.set("UserInfo", "uuid", login_data["id"])
        keyring.set_password("system", login_data["name"], login_data["access_token"])
        
        with open("creds.cfg", "w") as f:
            config.write(f)

    def slider_changed(self, slider):
        print(int(slider.get_value()))

    def switch_switched(self, switch, state):
        print(f"The switch has been switched {'on' if state else 'off'}")

    def install_mc(self, button):
        print("Installing Minecraft %s" % mc_ver )
        callback = {
            "setStatus": set_status,
            "setProgress": set_progress,
            "setMax": set_max
        }
        minecraft_launcher_lib.install.install_minecraft_version(mc_ver, minecraft_directory, callback=callback)
        print("Installed Minecraft ")

    def launch_mc(self, button):
        print("Launching minecraft")
        try:
            config.read("creds.cfg")
            options = {
                "username": config.get("UserInfo", "username"),
                "uuid": config.get("UserInfo", "uuid"),
                "token": keyring.get_password("system", config.get("UserInfo", "username"))
            }
        except Exception:
            options = {
                "demo": True
            }

        minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(mc_ver, minecraft_directory, options)
        subprocess.Popen(minecraft_command)
        if not self.check.get_active():
            print("Closing Launcher")
            self.close()

    def install_fabric(self, button):
        print("Installing fabric for Minecraft %s" % mc_ver)
        minecraft_launcher_lib.fabric.install_fabric(mc_ver, minecraft_directory)
        print("Installation for Fabric completed.")


class kreaLaunch(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.connect('activate', self.on_activate)

    def on_activate(self, app):
        self.win = MainWindow(application=app)
        self.win.present()


app = kreaLaunch(application_id="org.kreato.launcher")
app.run(sys.argv)
