from configparser import ConfigParser
from os.path import splitext, basename, join, isdir, relpath, abspath, split
from os import listdir,getcwd,system
from sys import argv

base_dir = None
start_with = None
show_file = None
ignore_file_name = None
show_extension = None
ignore_dir_name = None
ignore_pdf_dirname = None
ignore_pdf_filename = None
updated_pdf_files = None
pdf_write_mode = None

out_file_list = []
create_depth = -1

# 解决Nuitka打包后控制台输出中文乱码,看提示python3.8已上没这个问题，我用的是python3.7
system("chcp 65001 && cls")



def read_config():
    # \ 可以“换行”，表示上下两行是一行代码
    global base_dir, show_file, start_with, ignore_file_name, out_file_list, create_depth, show_extension, ignore_dir_name, \
        ignore_pdf_dirname, ignore_pdf_filename, updated_pdf_files, pdf_write_mode
    # exe 默认是在盘的local/temp，此时就拿不到相对路径下的config.ini
    # sys.argv解决该bug
    cf = ConfigParser()

    # cf.read("config.ini", encoding='utf-8') 作者原来的写法
    # 今天偶然发现在编辑器的终端执行修改过路径读取的exe会报错，直接运行则不会，又把作者的exe下载过来，发现无论直接运行还是cmd都不会报错
    # 以为是装了python有了相关环境的问题，把python卸载了也是如此，那么当初为啥运行不了，具体报错信息记不清了
    # 估计是作者的zip包的config.ini 配置不齐全导致的，而当时我对python完全不懂，也不知具体报错是啥了
    # zip包里的config.ini确实没和readme.md里配置一致，对python小白不友好，应该保证用户只需修改docsify项目跟目录就能运行，其他选项用户再看需求改动具体值
    # 不过为啥改过的在cmd会失败呢？有文章说是父进程之类的不同。。。。。；下面是改动的代码，现在还原回作者的代码，配置文件后缀就不改了
    # print("程序执行的当前路径:   " + split(argv[0])[0])
    # cf.read(split(argv[0])[0] + "\config.txt", encoding='utf-8')
    cf.read("config.txt", encoding='utf-8')
    base_dir = cf.get("config", "base_dir")
    print("程序运行的路径:   " + getcwd())
    print("项目的根路径base_dir:   " + base_dir)
    start_with = cf.get("config", "ignore_start_with").split("|")
    show_file = cf.get("config", "show_file").split('|')
    ignore_file_name = cf.get("config", "ignore_file_name").split("|")
    show_extension = bool(cf.get("config", "show_extension"))
    ignore_dir_name = cf.get("config", "ignore_dir_name").split("|")

    updated_pdf_files = cf.get("config", "updated_pdf_files").split("|")
    ignore_pdf_dirname = cf.get("config", "ignore_pdf_dirname").split("|")
    ignore_pdf_filename = cf.get("config", "ignore_pdf_filename").split("|")
    pdf_write_mode = int(cf.get("config", "pdf_write_mode"))

    out_file_list = cf.get("outFile", "eachFile").split("|")
    create_depth = int(cf.get("outFile", "create_depth"))


def check_file_extension(file_path):
    """
    检查文件后缀是否为指定的后缀
    :param file_path: 文件路径
    :return: 如果文件后缀为指定的后缀，返回True；否则返回False
    """
    file_extension = splitext(file_path)[1]
    if file_extension in show_file:
        return True
    else:
        return False


def check_file_name_satified(file_path):
    """
    获取文件名（不包括扩展名）
    :param file_path: 文件路径
    :return: 文件名（不包括扩展名）
    """
    file_name_with_extension = basename(file_path)
    file_name = splitext(file_name_with_extension)[0]
    if file_name[0] in start_with or file_name in ignore_file_name or file_name in ignore_dir_name:
        return False
    return True


def save_structure(root_dir, base_dir=base_dir, depth=0):
    """
    遍历指定目录及其所有子目录，生成并保存目录结构。
    :param root_dir: 要处理的根目录路径
    :param base_dir: 用来获得root_dir对base_dir的相对路径
    :param depth: 递归深度，文件夹深度
    """
    root = root_dir
    dirs = []
    files = []
    for item in listdir(root):
        if isdir(join(root, item)):
            dirs.append(item)
        else:
            files.append(item)
    subdir_structure = ''
    subdir_name = basename(root)

    if depth != 0:
        if create_depth == 0:
            subdir_structure += "- " + subdir_name + '\n'
        else:
            subdir_structure += "- [" + subdir_name + "](" + relpath(root, base_dir) + '\)\n'
    else:
        if create_depth == 0:
            subdir_structure += "- " + "首页" + '\n'
        else:
            subdir_structure += "- [" + "首页" + "](" + relpath(root, base_dir) + '\)\n'

    for file in files:
        if check_file_name_satified(join(root, file)):
            if check_file_extension(file):
                if show_extension:
                    fileName = file
                else:
                    fileName = splitext(file)[0]
                subdir_structure += "  " + "- [" + fileName + "](" + relpath(join(root, file), base_dir) + ')\n'

    for subdir in dirs:
        subdir_path = join(root, subdir)
        if check_file_name_satified(subdir_path):
            next_struct = save_structure(subdir_path, base_dir, depth + 1)
            # 子目录缩进。最后一项不缩进，是因为同级的目录得保持一致缩进（比如a和b同级，a下有a1,a2;a1,a2遍历完后开始遍历b，
            # 如果a2后面还缩进换行，那么此时b就和a2处于同一个缩进了，这样就不对了。
            next_struct = next_struct[:-1] if next_struct.endswith("\n") else next_struct
            next_struct = next_struct.replace("\n", "\n  ") + "\n"
            # 同级目录与文件保持相同缩进
            subdir_structure += "  " + next_struct

    back_struct = subdir_structure
    if depth == 1:
        subdir_structure = "- [" + "返回首页" + "](" + "" + '\?id=main)\n' + subdir_structure
    elif depth != 0:
        abs_pre_path = abspath(join(root, ".."))
        rel_pre_path = relpath(abs_pre_path, base_dir)
        subdir_structure = "- [" + "返回上一级" + "](" + rel_pre_path + '\)\n' + subdir_structure

    subdir_structure = subdir_structure.replace('\\', '/')
    print("%s : finished" % root_dir)
    if create_depth == -1:
        for file_name in out_file_list:
            with open(join(root, file_name), 'w', encoding="utf-8") as f:
                f.write(subdir_structure)
    else:
        if depth == 0:
            for file_name in out_file_list:
                with open(join(root, file_name), 'w', encoding="utf-8") as f:
                    f.write(subdir_structure)
    return back_struct


def change_pdf_to_md(root_dir, base_dir=base_dir):
    if (pdf_write_mode == 0):
        return
    for item in listdir(root_dir):
        filepath = join(root_dir, item)
        if isdir(filepath):
            if item in ignore_pdf_dirname:
                continue
            else:
                change_pdf_to_md(filepath, base_dir)
        else:
            file_name, file_extension = splitext(item)
            if ".pdf" == file_extension.lower():
                if pdf_write_mode == 1:
                    if item in updated_pdf_files:
                        write_pdf(base_dir, file_name, filepath, root_dir)
                else:
                    if item not in ignore_pdf_filename:
                        write_pdf(base_dir, file_name, filepath, root_dir)


def write_pdf(base_dir, file_name, filepath, root_dir):
    # md的文件名不能有空格，否则显示异常，这里重命名文件
    filepath_md = join(root_dir, file_name.replace(" ", "_") + ".md")
    content = "### " + file_name.replace(" ", "_") + "\n";
    content += "```pdf\n" + "     " + relpath(filepath, base_dir).replace("\\",
                                                                          "/") + "\n" + "```";
    with open(filepath_md, 'w', encoding="utf-8") as f:
        f.write(content)
    print(f'{file_name}.pdf 成功生成对应的MD!')


if __name__ == "__main__":
    read_config()
    change_pdf_to_md(base_dir, base_dir)
    save_structure(base_dir, base_dir, 0)
    input("侧边成功创建，请按回车键结束程序")
