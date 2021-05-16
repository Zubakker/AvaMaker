# This file is a part of the application.
# it allows the app to load thid-party presets for color scheme of AvaMaker

# You can load presets yourself you only need to add their filename without
# the extension in the __all__ variable of the __init__.py
# if you don't want to do it just type:
# >> python __modloader.py 
# in the command console

def main():
    from os import listdir
    current_dir_name = '/'.join(__file__.split('/')[:-1]) + '/'
    current_dir_content = listdir(current_dir_name)

    if current_dir_name == '/': # we check if the current dir is presets
        current_dir_name = ''
        current_dir_content = listdir()
    init = open(current_dir_name + '__init__.py', 'w')
    init.write('__all__ = [')
    for filename in current_dir_content:
        if filename.endswith('.py') and filename != '__init__.py' and \
                      filename != '__modloader.py' and filename != 'none.py':
            init.write('"' + filename[:-3] + '", ')
    init.write('"none"]')
    init.close()



if __name__ == '__main__':
    main()
