// enrichr API function
function enrich(options) {
    var defaultOptions = {
    description: "",
    popup: false
  };

  if (typeof options.description == 'undefined')
    options.description = defaultOptions.description;
  if (typeof options.popup == 'undefined')
    options.popup = defaultOptions.popup;
  if (typeof options.list == 'undefined')
    alert('No genes defined.');

  var form = document.createElement('form');
  form.setAttribute('method', 'post');
  form.setAttribute('action', 'http://amp.pharm.mssm.edu/Enrichr/enrich');
  if (options.popup)
    form.setAttribute('target', '_blank');
  form.setAttribute('enctype', 'multipart/form-data');

  var listField = document.createElement('input');
  listField.setAttribute('type', 'hidden');
  listField.setAttribute('name', 'list');
  listField.setAttribute('value', options.list);
  form.appendChild(listField);

  var descField = document.createElement('input');
  descField.setAttribute('type', 'hidden');
  descField.setAttribute('name', 'description');
  descField.setAttribute('value', options.description);
  form.appendChild(descField);

  document.body.appendChild(form);
  form.submit();
  document.body.removeChild(form);
}


$(document).ready(function(){
  $.blockUI({ css: { 
    border: 'none', 
    padding: '15px', 
    backgroundColor: '#000', 
    '-webkit-border-radius': '10px', 
    '-moz-border-radius': '10px', 
    opacity: .8, 
    color: '#fff' 
  } });
  // display the statsArray in the left division underneath the LCD1000 button
  $.each(statsArray, function(index, dic){
    for (x in dic){
    var statsBase = "<p class = 'study-stats' align= 'left'>" + "<strong>" + x + "</strong>" +": " + dic[x] + "</p>";
    // console.log(statsBase);
    $(".stats-div").append(statsBase);
    };
  });

  //when enrichr button pressed, send the consensus genes to the enrichr website
	$(".enrichr-up .enrichr_btn").on ("click", function(){
		enrich({list:gene_array_up, description: "up", popup:true})		
	});
	$(".enrichr-dn .enrichr_btn").on ("click", function(){
		enrich({list:gene_array_dn, description: "down", popup:true})		
	});
  //when the l1000cds button pressed, send the up and down consensus genes to l1000cds API
  $(".l1000cds_btn").on ("click", function(){
    console.log("clicked");
    // var baseurl = "http://amp.pharm.mssm.edu/L1000CDS2/query";
    var data = {"upGenes": geneUpArray, "dnGenes": geneDnArray};
    // console.log(geneUpArray);
    var config = {"aggravate":false,"searchMethod":"geneSet",share:true};
    // var metadata = [{"key":"Tag","value":"gene-set python example"},{"key":"Cell","value":"MCF7"}];
    var payload = {data:data,config:config};
    $.ajax({
      url: 'http://127.0.0.1:5050/L1000CDS', 
      data: JSON.stringify(payload),
      method: 'POST',
      contentType: 'application/json',
      success: function(results){
          var baseurl = "http://amp.pharm.mssm.edu/L1000CDS2/#/result/";
          // console.log(typeof(results));
          window.open(baseurl+results);
          }    
       }).fail(function(){
        alert("error");
      });
  });
  
    make_d3_clustergram(d3_json_data);
    $.unblockUI();
  	$('.btn-reset').on('click', function(){
      console.log('reset');
      make_d3_clustergram(d3_json_data);
    });
});











