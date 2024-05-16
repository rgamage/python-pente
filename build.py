# Build script to build pente program

import os, ConfigParser, string

os.chdir("d:\\gamoto\\python\\pente")

#Read config file, get versions and increment the build number
cp = ConfigParser.ConfigParser()
f1 = open("pente.cfg","r+")
cp.readfp(open('pente.cfg'))
#increment build number in cfg file
cp.set("Versions","build",str(cp.getint("Versions","build")+1))
#get build number from cfg file
build = cp.getint("Versions","build")
#get minor & major versions from source code comments
f2 = open("pente.py","r")
s = f2.readlines()
f2.close()
for line in s:
    i = string.find(line,"Current Major Version =")
    if i>0:
        major = int(line[i+23:])
    i = string.find(line,"Current Minor Version =")
    if i>0:
        minor = int(line[i+23:])
#store these version numbers in cfg file
cp.set("Versions","majorversion",str(major))
cp.set("Versions","minorversion",str(minor))
#save cfg file
cp.write(f1)
#close cfg file
f1.close()
#construct full version string
version =  "%d.%02d.%02d" % (major,minor,build)
#construct file name
fname = "pente_" + version + ".py"
#construct path name
fpath = os.path.join("archive",fname)
#save archive copy of source code
f=open(fpath,"w")
f.writelines(s)
f.close()

#now do the actual build
os.system("python setup.py py2exe")

#now build the setup.exe file
files = os.listdir("deploy")
delfiles = []
for file in files:
   if string.find(file,".exe"):
   	delfiles.append(file)  #build list of .exe files, to delete on ftp server
os.system("del deploy\*.exe")  #now delete them in our local folder
os.system('"C:\Program Files\Inno Setup 5\Compil32.exe" /cc pente.iss')  #delete previous self-exe archives
zipname = "pente_%d_%02d_%02d_Install_Win32.exe" % (major,minor,build)
os.system("rename deploy\setup.exe " + zipname)

#zipname = "pente_4_5_6_Windows_Install.exe"
#now create a weblink include file
s = 'Windows Install File: <a href="code/%s">%s</a>' % (zipname,zipname)
f = open("deploy/pente.shtml",'w')
f.write(s)
f.close()

#now ftp the setup file and weblink file to the web server
import ftplib
ftp = ftplib.FTP("psi.pair.com")
ftp.login("rgamage", "August07")
ftp.cwd("public_html/gamages/randy/includes")
ftp.storbinary("STOR " + "pente.shtml", open("deploy/pente.shtml", "rb"), 1024)
ftp.cwd("../code")
#for file in delfiles:
#    ftp.delete(file)
print "Uploading Windows Binary to FTP site:"
ftp.storbinary("STOR " + zipname, open("deploy/" + zipname, "rb"), 1024)
ftp.quit()



