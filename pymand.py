from flask import Flask, url_for, request, json, jsonify
from requests.utils import quote
import subprocess, sys, traceback, datetime

app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Welcome'

@app.route('/_1/get_and_print', methods = ['POST'])
def api_get_and_print():
    if request.headers['Content-Type'] == 'application/json':
        jsonRequest = json.loads(request.data)
        
        printer = jsonRequest['printer']
        pdfUrl = jsonRequest['pdfUrl']
        jobName = '{:%y-%m-%d_%H:%M:%S.%f}'.format(datetime.datetime.now())[:-3]+"_"+jsonRequest['jobName'].replace(" ", "_")
#        print "printing on "+jsonRequest['printer']+" job "+jobName+": "+pdfUrl

        lpResult = ''
        status = 500
        try:
            safeUrl = quote(pdfUrl,safe="%/:=&?~#+!$,;'@()*[]")
	        #baseEnd = pdfUrl.find("?")
	        #print baseEnd
	        #if baseEnd > 0:
	        #	safeUrl = pdfUrl[:baseEnd+1]+quote(pdfUrl[baseEnd+1:],safe="%/:=&?~#+!$,;'@()*[]")
	        #else:
		    #safeUrl = pdfUrl
            print "printing on "+jsonRequest['printer']+" job "+jobName+": "+safeUrl
            lpResult = subprocess.check_output(
                "curl \""+safeUrl+"\"|lp -d "+printer+" -t "+jobName+"", 
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
        resp = jsonify({'response': 'Unsupported Media Type :('})
        resp.status_code = 415
        return resp

@app.route('/_1/printers', methods = ['POST'])
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


if __name__ == '__main__':
    app.run(host='0.0.0.0')
