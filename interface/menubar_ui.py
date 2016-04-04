# -*- coding: utf-8 -*-
#!/usr/bin/python3

UI_INFO = """<?xml version="1.0"? encoding="UTF-8"?>
<interface>
  <menu id="menubar">
    <submenu>
      <attribute name="label">Fichier</attribute>
      <section>
        <item>
          <attribute name="label">Afficher les fichiers sauvegardés</attribute>
          <attribute name="action">win.show_saved</attribute>
        </item>
        <item>
          <attribute name ="label">Préférences</attribute>
          <attribute name ="action">win.settings</attribute>
        </item>
        <item>
          <attribute name ="label">Quitter</attribute>
          <attribute name ="action">app.quit</attribute>
        </item>
      </section>
    </submenu>
    <submenu>
      <attribute name="label">Action</attribute>
      <section>
        <item>
          <attribute name="label">Démmarer le scan</attribute>
          <attribute name="action">win.start_watching</attribute>
        </item>
        <item>
          <attribute name ="label">Arrêter le scan</attribute>
          <attribute name="action">win.stop_watching</attribute>
        </item>
        <item>
          <attribute name ="label">Scanner maintenant</attribute>
          <attribute name="action">win.watch_now</attribute>
        </item>
      </section>
    </submenu>
    <submenu>
      <attribute name="label">Aide</attribute>
      <section>
        <item>
          <attribute name="label">À propos</attribute>
          <attribute name="action">win.about</attribute>
        </item>
      </section>
    </submenu>
  </menu>
</interface>
"""
