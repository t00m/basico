rm -rf basico.egg-info build dist
pip3 uninstall basico -qy
#~ pip3 uninstall kb4it -qy
python3 setup.py install --user
read -n1 -r -p "Press any key to continue..." key
reset && $HOME/.local/bin/basico
