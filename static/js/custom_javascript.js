// enrichr API function adapted from the enrichr website
// it takes a list of genes and send it to enrichr to open a new window to show the resulting query
//if popup is set to be true
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



/* Formatting function for row child - modify as you need */
// This function is too verbose, needs improvement 
function format ( d ) {
    // `d` is the original data object for the row
    if (d.up_genes !== "platform not supported"){
        return '<table cellpadding="5" cellspacing="0" class="childclass childclass2" style="padding-left:50px; border:none">'+
            '<tr>'+
                '<td>Extra info:</td>'+
                '<td>'+d.study_description+'</td>'+
                '<td><button class="SOFTfile_btn btn btn-default btn-sm" data-toggle="tooltip" data-placement="bottom" title="download cleaned SOFT file">' +
                '<span class= "glyphicon glyphicon-new-window" aria-hidden="true"></span></button></td>'+
            '</tr>'+
            '<tr>'+
                '<td>Age of organism:</td>'+
                '<td>'+d.Age_of_organism+'</td>'+
                '<td></td>'+
            '</tr>'+
            '<tr>'+
                '<td>Up genes:</td>'+
                '<td>'+d.up_genes.slice(0,10).map(function(item){return item[0]}).join(' ')+'...</td>'+
                '<td><button class="btn btn-danger btn-sm up_gene">Enrichr</button></td>'+
            '</tr>'+
            '<tr>'+
                '<td>Down genes:</td>'+
                '<td>'+d.down_genes.slice(0,10).map(function(item){return item[0]}).join(' ')+'...</td>'+
                '<td><button class="btn btn-primary btn-sm down_gene">Enrichr</button></td>'
            '</tr>'+         
        '</table>';
    }else{
        return '<table cellpadding="5" cellspacing="0" class="childclass childclass2" style="padding-left:50px; border:none">'+
            '<tr>'+
                '<td>Extra info:</td>'+
                '<td>'+d.study_description+'</td>'+
                '<td><button class="SOFTfile_btn btn btn-default btn-sm" data-toggle="tooltip" data-placement="bottom" title="download cleaned SOFT file">' +
                '<span class= "glyphicon glyphicon-new-window" aria-hidden="true"></span></button></td>'+
            '</tr>'+
            '<tr>'+
                '<td>Age of organism:</td>'+
                '<td>'+d.Age_of_organism+'</td>'+
                '<td></td>'+
            '</tr>'+
            '<tr>'+
                '<td>Up genes:</td>'+
                '<td>'+d.up_genes+'</td>'+
                '<td><button class="btn btn-danger btn-sm up_gene">Enrichr</button></td>'+
            '</tr>'+
            '<tr>'+
                '<td>Down genes:</td>'+
                '<td>'+d.down_genes+'</td>'+
                '<td><button class="btn btn-primary btn-sm down_gene">Enrichr</button></td>'+
            '</tr>'+         
        '</table>';
    }

}

// setup tabledata
// this uses the datatalbe API, read the online documentation carefully
$(document).ready(function() {
    // $('[data-toggle="tooltip"]').tooltip(); //activate bootstrap tooltip function
    var table = $('#example').DataTable( {
        "ajax": "data/tabledata.txt",
        "autoWidth":true,
        // "scrollY": "600px",
        "paging":true,
        "columnDefs":[
            {"width": "2%", "targets": 0},
            {"width": "6%", "targets": 1},
            {"width": "6%", "targets": 2},
            {"width": "15%", "targets": 3},
            {"width": "6%", "targets": 4},
            {"width": "6%", "targets": 5},
            {"width": "20%", "targets": 6},
            {"width": "5%", "targets": 7},
            {"width": "5%", "targets": 8},
            {"width": "7%", "targets": 9},            
            {"width": "10%", "targets": 10},
            {"width": "3%", "targets": 11}
        ],
        "columns": [
            {
                "className":"details-control showchild",
                "orderable":      false,
                "data":           null,
                "defaultContent": ""
            },
            {"data": "GSE_number",
            "className": "GEO_link"
            },
            {"data": "GDS_number",
            "className": "showchild"},
            {"data": "array_type",
            "className": "array_column showchild"
            },
            {"data": "platform",
            "className": "showchild"},
            {"data": "organism",
            "className": "showchild"},            
            {"data": "tissue_type",
            "className": "tissue_column showchild"
            },
            {"data": "disease",
            "className": "showchild"},
            {"data": "manipulated_gene", 
            "className": "showchild"},
            {"data": "perturbation", 
            "className": "showchild"},
            {"data": "platform_status"},
            {"data": null,
            "orderable": false,
            "defaultContent": "<input type='checkbox' class='checked_data'>"}
        ],
        "order": [],    
    });
    
    // link to the GEO website    
    $('#example tbody').on( 'click', 'td.GEO_link', function () {    
        window.open('http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + table.cell( this ).data());
    });

    // link to the enrichr website
    $('#example tbody').on( 'click', 'button.up_gene', function () { 
        try {    
            var tr = $(this).parent().parent().parent().parent().parent().parent().prev('tr');        
            var upgene_list = table.row(tr).data().up_genes.map(function(item){return item[0]}).join("\n");
            var descript = table.row(tr).data().study_description;
            enrich({list:upgene_list, description: descript+"_up", popup:true})
        }
        catch(e){
            alert("Platform Not Supported!");
        };
    });

    $('#example tbody').on('click', 'button.down_gene', function () {
        try {    
            var tr = $(this).parent().parent().parent().parent().parent().parent().prev('tr')        
            var downgene_list = table.row(tr).data().down_genes.map(function(item){return item[0]}).join("\n");
            var descript = table.row(tr).data().study_description
            enrich({list:downgene_list, description: descript+"_down", popup:true})
        }
        catch(e){
            alert("Platform Not Supported!")
        };
    });

    //link to a cleaned SOFT file shown on website
    $('#example tbody').on('click','.SOFTfile_btn', function(){
        baseurl = 'http://amp.pharm.mssm.edu/g2e/';        
        var tr = $(this).parent().parent().parent().parent().parent().parent().prev('tr');
        var file_url = table.row(tr).data().file_url;
        if (file_url !== "platform not supported"){
            window.open(baseurl+file_url);
        }else{
            alert("Platform Not Supported");
        };
    });

    // Add event listener for opening and closing details (childrow)
    $('#example tbody').on('click', '.showchild', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
 
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );
    //add event listener to the checkbox
    //when checkbox is clicked, it addes or removes a class called 'selected' to the row
    $('#example tbody').on('click', '.checked_data', function(){
        $(this).parent().parent().toggleClass('selected'); 
    });

    //when the clear button is clicked, remove all the selected class of the rows
    $('#clear').on('click', function(){
        $('.checked_data').attr('checked', false);
        $('.selected').removeClass('selected');

    });

    //when the submit button is clicked, collect all the rows that have 'selected' class
    //and organize the selected study into an array of study dictionaries.  
    $('#submit').on('click', function(){
        //blocks the screen of the index page when the data is being sent and calculated at the backend
        $.blockUI({ css: { 
            border: 'none', 
            padding: '15px', 
            backgroundColor: '#000', 
            '-webkit-border-radius': '10px', 
            '-moz-border-radius': '10px', 
            opacity: .8, 
            color: '#fff' 
            } });
        // send data to the server. server processes the data and send it back
        var senddata = [];
        var allRows = table.rows('.selected').data()
        console.log(allRows.length);
        platform_check = true; //check to see if one or more studies are not suppported
        if ((allRows.length) != 0){
            try{
                table.rows('.selected').every(function(){
                    var studyIndex = (table.row(this).index());
                    var up_genes_ls = this.data().up_genes;
                    var down_genes_ls = this.data().down_genes;
                    var GSENum = this.data().GSE_number;
                    var tissueType = this.data().tissue_type;
                    var studyDescript = this.data().study_description;
                    var perturbation = this.data().perturbation;        
                    if (up_genes_ls != "platform not supported"){
                        var study_dict = {'up_genes': up_genes_ls,
                                            'down_genes': down_genes_ls,
                                            'GSENum': GSENum,
                                            'tissueType': tissueType,
                                            'studyDescript': studyDescript,
                                            'perturbation': perturbation,
                                            'studyIndex': studyIndex
                                        };
                        senddata.push(study_dict);
                    }else{
                        platform_check = false;
                        }
                    });
                console.log(senddata);
                if (platform_check){
                    $.ajax({
                        url: 'http://127.0.0.1:5050/results', 
                        data: JSON.stringify(senddata),
                        method: 'POST',
                        contentType: 'application/json',
                        success: function(results){
                            // console.log(results);
                            window.open(results);
                            $.unblockUI();        
                            }
                        });
                }else{
                    alert("One or more platforms from selected studies are not supported!");
                    }   
            }catch (e){
                console.log(e);
            }
                    // else{
                    //     alert("One or more studies' platforms are not supported!")
                    // }                
        }else{
            alert('No Study Selected');
        };   
    });







} );