from flask import Flask, url_for, request, json, jsonify
from requests.utils import quote
import subprocess, sys, traceback, datetime
import uuid

def pymand():
    print 'Starting'
    tmpdir = "/tmp/pymand.tmp/"
    save_tmp_file = True
    app = Flask(__name__)

    @app.route('/')
    def api_root():
        return 'Welcome'

    @app.route('/api/get_and_print', methods = ['POST'])
    def api_get_and_print():
        print "get_and_print"
        if request.headers['Content-Type'].startswith( 'application/json'):
            jsonRequest = json.loads(request.data)
            
            try:
                param = 'printer'
                printer = jsonRequest[param]
                param = 'url'
                doc_url = jsonRequest[param]
                param = 'jobName'
                jobName = jsonRequest[param]
            except:
                data = {
                    'msg'  : 'missing parameter '+param
                }
                resp = jsonify(data)
                resp.status_code = 418
                print "Error printing : 418 - "+'missing parameter '+param
                return resp 
                
            
            jobName = '{:%y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3]+"-"+str(uuid.uuid4())[:8]+"_"+jobName.replace(" ", "_").replace("/", "_")

            lpResult = ''
            status = 500
            try:
                safeUrl = quote(doc_url,safe="%/:=&?~#+!$,;'@()*[]-")
                if save_tmp_file:
                    fileName = quote(jobName,safe="%/:=&?~#+!$,;'@()*[]-")+".pdf"
                    cmdUrl = "curl -H 'Accept-Language: it' --create-dirs -o "+tmpdir+fileName+" \""+safeUrl+"\" && lp -d "+printer+" -t "+jobName+" "+tmpdir+fileName
                else:
                    cmdUrl = "curl -H 'Accept-Language: it' \""+safeUrl+"\"|lp -d "+printer+" -t "+jobName+""
                print "printing on "+jsonRequest['printer']+" job "+jobName+": "+safeUrl
                lpResult = subprocess.check_output(
                    cmdUrl, 
                    stderr=subprocess.STDOUT,
                    shell=True)
                status = 200
            except IOError as e:
                lpResult = "I/O error({0}): {1}".format(e.errno, e.strerror)
                print "I/O error({0}): {1}".format(e.errno, e.strerror)
            except subprocess.CalledProcessError as cpe:
                lpResult = cpe.output
                print cpe.output
            except Exception as er2:
                lpResult = "Error printing " ,traceback.format_exception(*sys.exc_info())
                print "Error printing " ,traceback.format_exception(*sys.exc_info())
            except:
                lpResult = "Unexpected error:", sys.exc_info()[0]
                print "Unexpected error:", sys.exc_info()[0] 
            data = {
                'response'  : lpResult,
                'jobName' : jobName
            }
            resp = jsonify(data)
            resp.status_code = status
            return resp

        else:
            msg = 'Unsupported Media Type :( --- '+request.headers['Content-Type']
            resp = jsonify({'response': msg})
            resp.status_code = 415
            return resp

    @app.route('/api/printers', methods = ['POST'])
    def printers():
        outp = subprocess.check_output("lpstat" + " -a", shell=True)
        #print outp.split('\n')
        printerList = []
        for i, val in enumerate(outp.split('\n')):
            if val:
                len = val.find(" ")
                printerList.append(
                    {
                        'name':val[:len],
                        'status': val[len+1:]
                    }
                )
        resp = jsonify({'printers': printerList})
        resp.status_code = 200
        return resp


    #if __name__ == '__main__':
    #    app.run(host='0.0.0.0', threaded=True)

    app.run(host='0.0.0.0', threaded=True)
pymand()
