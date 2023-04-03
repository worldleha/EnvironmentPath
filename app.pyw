from environment_path import *
import asyncio
import concurrent.futures
import sys,ctypes
import os.path

from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView


async def read_all(reader):
    header_bs = bytearray()

    while header_bs[-4:] != b"\r\n\r\n" and len(header_bs)<1000:
        header_bs += await reader.read(1)
    if len(header_bs)>=1000:
        return ({},"")
    print(header_bs)
    header_dict = {}
    for item in header_bs.split(b"\n"):
        if len(item)>3 and b":" in item:
            items = item.split(b":")
            key = items[0].decode()
            value = items[1].decode()
            header_dict[key] = value
    
    content_bs = bytearray()
    if "Content-Length" in header_dict:
        content_bs += await reader.read(int(header_dict["Content-Length"]))
    return (header_bs, content_bs)



async def send_message(writer, content):
    status_message = 'HTTP/1.1 200 OK\n'
    header_message = f'''Content-Type:text/html;charset=UTF-8
Server:Tengine/1.4.6
Access-Control-Allow-Origin:*
Access-Control-Allow-Methods:POST
Content-Length:{len(content)}
Connection:close
'''
    end_message = '\n'+content
    writer.write((status_message+header_message+end_message).encode())
    await writer.drain()

async def response(reader, writer):
    
    print("enter")
    header, content = await read_all(reader)
    request = header.split(b" ")[1].decode()
    print(request)
    match(request):
        case "/show":
            with EnvironmentPath() as ep:
                pathList = ep.ListPath()
                await send_message(writer, ";".join(pathList))
            print("exit")
        case "/selectpath":
            path = QFileDialog.getExistingDirectory(browser,"choose directory",".")
            await send_message(writer, path)
            
        case "/":
            try:
                with EnvironmentPath() as ep:
                    pathList = ep.ListPath()
                    with open("save.txt", "a+") as f:
                        f.write("\n".join(pathList) +"\n" +"="*30)

                    ep.pathList = content.decode().split(";")
                    ep.ChangePath()
                    await send_message(writer, "success")
            except:
                await send_message(writer, "error")
            
            print("exit")

        
async def create_server():
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        client = loop.run_in_executor(
            pool, create_window)
        
        server_cor = asyncio.start_server(response, "127.0.0.1", 8840, limit = 2**24)
        server = await server_cor
        await client
        #async with server:
        #    await server.serve_forever()


def Qabs_url(filename):
    abs_url = "file:///" + os.path.abspath(filename).replace("\\",'/')
    print(abs_url)
    return QUrl(abs_url)

def alertM(this):
    self = this
    def alertP(title, message):
        QMessageBox.about(self, title, message)
    return alertP

def create_window():
    global browser
    app = QApplication(sys.argv)
    browser = QWebEngineView()
    browser.setWindowIcon(QIcon('head.ico'))
    browser.setFixedSize(410,620)
    browser.setWindowTitle(u'环境变量Path修改器')
    #browser.setWindowFlags(Qt.WindowMinimizeButtonHint)
    
    #with open("change.html", "r", encoding = "utf8") as f:
    #    browser.setHtml(f.read())
    
    browser.load(Qabs_url("change.html"))
    browser.alert = alertM(browser)
    browser.show()
    app.exec_()
    exit(0)
    
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
if __name__ == "__main__":

    
    
    if is_admin():
        
        
        asyncio.run(create_server())
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)        
    
