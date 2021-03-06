<!DOCTYPE HTML>
<html>
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>${hda.name} | ${visualization_name}</title>

## ----------------------------------------------------------------------------
<link type="text/css" rel="Stylesheet" media="screen" href="/galaxy-pdacs-dev/static/style/base.css">
<link type="text/css" rel="Stylesheet" media="screen" href="/galaxy-pdacs-dev/plugins/visualizations/graphview/static/graphview.css">

## ----------------------------------------------------------------------------
<script type="text/javascript" src="/galaxy-pdacs-dev/static/scripts/libs/jquery/jquery.js"></script>
<script type="text/javascript" src="/galaxy-pdacs-dev/static/scripts/libs/jquery/jquery.migrate.js"></script>


</head>

## ----------------------------------------------------------------------------
<body>
%if not embedded:
## dataset info: only show if on own page
<div id="chart-header" class="header">
    <h2 class="title">Gnuplot</h2>
    <div id="tooltip"></div>
    <!-- <p class="subtitle">${hda.info}</p> -->
</div>
%endif

<table class="noborder" style="width:99%"> 

  <tr><td>
    <div style="float:right"><a id="saveplot" href="" download="plot.svg"><img src="/galaxy-pdacs-dev/plugins/visualizations/gnuplot/static/download-icon.png" alt="Download SVG" width="30"></a></div>
    <img src="" id="gnuimg" type="image/svg+xml" width="100%" style="min-height:300px; max-height:800px" class="float-right"/>
  </td></tr>
  <tr>
    <td valign=top style="width:99%;">
      <div style="float:left"><button type="button" onclick="scriptChange()" class="btn btn-primary" style="margin-left:auto;margin-right:auto">Plot</button></div>
      <div style="float:right" id="PROGRESS">Uninitialized</div><div style="clear:both"></div>              
      <textarea class="emscripten" id="gnuplot" rows="10" style="width:100%" >
# Note: do not change the output / terminal line; this page is looking for a file named out.svg generated by gnuplot.
set terminal svg enhanced size 700,500 
set output 'out.svg'
</textarea>

      <textarea id="output" rows="8" style="width:100%"></textarea>
    </td>
  </tr>
</table>

<iframe id="hiddenDownloader" style="display:none;"></iframe>

<script src='/galaxy-pdacs-dev/plugins/visualizations/gnuplot/static/gnuplot_api.js'></script> 
<script>
  function scriptChange() {
    isInError=0;
    var val = document.getElementById("gnuplot").value;
    if (lastTAContent == val)
      return;
    document.getElementById('PROGRESS').innerHTML = 'Generating plot';
    localStorage["gnuplot.script"] = val;
    if (gnuplot.isRunning) {
        //setTimeout(scriptChange, 1000);
    } 
    else 
    {
      lastTAContent = val;
      runScript();
    }
  };

  var processFiles = function() {
    for( var x in fnames )
    {
      console.log("fname test: " + fnames[x][0] + " " + '${hda.name}')
      if( fnames[x][0] == '${ hda.hid } ${ hda.name }' )
      {
        plot_line += '\n'
      }
      else
      {
        plot_line += '\n#'
      }
      var is_firefox = /firefox/i.test(navigator.userAgent)
      if(is_firefox) 
      {
        plot_line +=  'plot "' + fnames[x][0] + '" with lines';
        uber_plot_line += '"' + fnames[x][0] + '" with lines,';
      }
      else
      {
        plot_line +=  'plot "' + fnames[x][0] + '"';
        uber_plot_line += '"' + fnames[x][0] + '",';
      }

    }
    document.getElementById('gnuplot').value = document.getElementById('gnuplot').value + plot_line;
    document.getElementById('gnuplot').value = document.getElementById('gnuplot').value + uber_plot_line;
    document.getElementById('PROGRESS').innerHTML = 'Loading files';

    var loaded_matpower=0;
    var idx=0;
    {
      var xhr = new XMLHttpRequest();
      var fileReader = new FileReader();
      fname=fnames[idx];


      xhr.open("GET", fname[1], true);
      // Set the responseType to blob
      xhr.responseType = "blob";
      xhr.addEventListener("error", function () {
        console.log("got error: " + xhr.status);
      }, false);

      xhr.addEventListener("load", function () {
        // console.log("got status: " + xhr.status)
        if (xhr.status === 200) {
            // onload needed since Google Chrome doesn't support addEventListener for FileReader
          fileReader.onload = function (evt) 
          {
            // Read out file contents as a Data URL
            var result = evt.target.result;  
            // Store Data URL in localStorage
            try {
              if (evt.target.result) {
                gnuplot.onOutput("Reading file: " + fname[0] + " (" + evt.target.result.length + " bytes)");
                files[fname[0]] = evt.target.result;
              }
              idx=idx+1;
              if( idx < fnames.length ) {
                fname=fnames[idx];
                console.log("reading file: " + fname[1] );
                percentFinished = Math.floor(100*idx/fnames.length);
                document.getElementById('PROGRESS').innerHTML = 'Loading files: ' + percentFinished + '%';

                xhr.open("GET", fname[1], true);
                xhr.send();
              }
              else
              {
                //localStorage["gnuplot.files"] = JSON.stringify(files);
                document.getElementById('PROGRESS').innerHTML = 'Loading files: 100%';
                document.getElementById('PROGRESS').innerHTML = 'Generating plot';
                scriptChange();
              }
            }
            catch (e) {
              console.log("Storage failed: " + e);
            }
          };
          // Load blob as Data URL
          fileReader.readAsText(xhr.response);
        }
      }, false);

      // Send XHR
      xhr.send();
    }
  }

  var runScript = function() {
    var editor = document.getElementById('gnuplot');   // textarea
    var start = Date.now();
    // "upload" files to worker thread

    for (var f in files)
      gnuplot.putFile(f, files[f]);
      gnuplot.run(editor.value, function(e) {
      document.getElementById('PROGRESS').innerHTML = 'Fetching plot';
      gnuplot.onOutput('Execution took ' + (Date.now() - start) / 1000 + 's.');
      gnuplot.getFile('out.svg', function(e) {
        if (!e.content) {
          gnuplot.onError("Output file out.svg not found!");
          return;
        }
        saveplot=document.getElementById('saveplot');
        saveplot.href=""
        var img = document.getElementById('gnuimg');
        if(isInError)
        {
            document.getElementById('PROGRESS').innerHTML = 'Error generating plot';
            img.src = '/galaxy-pdacs-dev/plugins/visualizations/gnuplot/static/imageNotFound.jpg'
            return;
        }

        try {
          var ab = new Uint8Array(e.content);
          var blob = new Blob([ab], {"type": "image\/svg+xml"});
            // console.log("window url");
            window.URL = window.URL || window.webkitURL;
            img.src = window.URL.createObjectURL(blob);
            document.getElementById('PROGRESS').innerHTML = 'Finished plot';


            // update download link
            saveplot.href=img.src;

            setTimeout(clearProgress, 1000);
        } catch (err) { // in case blob / URL missing, fallback to data-uri
          if (!window.blobalert) {
            alert('Warning - your browser does not support Blob-URLs, using data-uri with a lot more memory and time required. Err: ' + err);
            window.blobalert = true;
          }
          var rstr = '';
          for (var i = 0; i < e.content.length; i++)
            rstr += String.fromCharCode(e.content[i]);
          img.src = 'data:image\/svg+xml;base64,' + btoa(rstr);
        }
      });
    });
  };

  // set the script from local storage
  // if (localStorage["gnuplot.script"])
  //     document.getElementById('gnuplot').value = localStorage["gnuplot.script"];
  // scriptChange();
  function clearProgress() {
    document.getElementById('PROGRESS').innerHTML = '';
  }

  var isInError = 0;
  gnuplot = new Gnuplot('/galaxy-pdacs-dev/plugins/visualizations/gnuplot/static/gnuplot.js');
  gnuplot.onOutput = function(text) {
    document.getElementById('output').value += text + '\n';
    document.getElementById('output').scrollTop = 99999;
    if( text == "Exit Status: 1" )
    {
      console.log("THIS IS AN ERROR, updating message");
      isInError=1;
    }
  };
  gnuplot.onError = function(text) {
    console.log("in onError");
    document.getElementById('output').value += 'ERR: ' + text + '\n';
    document.getElementById('output').scrollTop = 99999;
  };
  var lastTAContent = ''; 

  files = {};
  var plot_line = "";
  var uber_plot_line = "\n#plot ";
  var fnames = [];
  var request = $.ajax({
    type: "GET",
    url: "/galaxy-pdacs-dev/api/histories/${trans.security.encode_id( hda.history.id )}/contents",
    data: { }
  });
  request.done(function( msg ) {
      //console.log("Received data: " + msg );
      for( var x in msg )
      {
          console.log("msg: ", msg[x] );
          if( msg[x]['state'] == "ok" && msg[x]['ext']=='csv' && !msg[x]['deleted'])
          {
            var url = '/galaxy-pdacs-dev/datasets/' + msg[x]['id'] + '/display?to_ext=tabular'
            fnames.push( Array( msg[x]['hid'] + " " + msg[x]['name'], url ) );
          }

      }
      processFiles();
    });
  request.fail(function( j,t ) {
      console.log("Error: " + t );
      document.getElementById('PROGRESS').innerHTML = 'Error generating plot';
      var img = document.getElementById('gnuimg');
      img.src = '/galaxy-pdacs-dev/plugins/visualizations/gnuplot/static/imageNotFound.jpg'
    });

    </script>
</body>
