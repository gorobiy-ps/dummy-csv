$(document).ready(function(){
  console.log('START JS');
  rebind();
});

function rebind(){
  $('.type-select').unbind();
  $('button[name="generate"]').unbind();
  extra_data_view_handler();
  generate_csv();
  check_pending();
}

function check_pending(){
  var tasks = $('.badge.pending');
  if (tasks.length > 0){
    var delay = 1500;
    $.each(tasks, function(index, item){
      get_status(item, delay);
    });
  }
}

function get_status(item, delay){
  $.ajax({
    method:'POST',
    url: 'check_task_status',
    data: {
      task_id: $(item).attr('data-iden'),
      csrfmiddlewaretoken: getCookie('csrftoken')
    },
    dataType: 'json'
  }).done(function(response){
    if (response.status){
      var parent_td = $(item).parent();
      parent_td.html('<span class="badge bg-success">Ready</span>');
      html_str = '<a href="/download_file/'+response.link+'" download="'+response.link+'">Download</a>';
      parent_td.parent().find('.actions').html(html_str);
    } else {
      delay = parseInt(delay * 1.2);
      setTimeout(get_status, delay, item, delay);
    }
  });
}

function generate_csv(){
  $('button[name="generate"]').click(function(){
    var schema_id = parseInt($('#schema-id').val());
    var rows_quantity = parseInt($('#rows-quantity').val());
    if ((schema_id > 0) && (rows_quantity > 0)){
      $.ajax({
        method:'POST',
        url: 'put_csv',
        data: {
          schema_id: schema_id,
          rows_quantity: rows_quantity,
          csrfmiddlewaretoken: getCookie('csrftoken')
        },
        dataType: 'json'
      }).done(function(response){
        if (response.status){
          window.location = response.redirect;
        } else {
          alert(response.message);
        }
      });
    } else {
      alert('Put valid data, please');
    }
  });
}

function extra_data_view_handler(){
  views = {
    0: 'empty',
    1: 'empty',
    2: 'empty',
    3: 'mask',
    4: 'range',
    5: 'range'
  }

  $('.type-select').change(function(){
    var parent_row = $(this).parents('.row');
    var iden = parent_row.attr('data-iden');
    var container = parent_row.find('.extra-options')
    var type = views[$(this).val()];
    snippen_view(iden, container, type)
  });
}

function snippen_view(iden, container, type){
  if (type == 'mask' || type == 'range'){
    $.ajax({
      method:'POST',
      url: 'get_snippet',
      data: {
        data_iden: iden,
        type: type,
        csrfmiddlewaretoken: getCookie('csrftoken')
      },
      dataType: 'json'
    }).done(function(response){
      container.html(response.html);
    });
  } else {
    container.html('');
  }
}

function add_column(self){
  var row_container = $(self).parents('.row');
  var selects = row_container.find('select');
  var selects_data = {};
  $.each(selects, function(i, item){
    selects_data[$(item).attr('name')] = $(item).val();
  });
  var row_to_insert = row_container.clone();
  var iden = choose_iden();
  row_to_insert
    .addClass('d-none')
    .removeClass('card-body')
    .attr('data-iden',iden);
  row_to_insert.adjust_form(iden, selects_data);
  $('#schema-form').append(row_to_insert);
  row_to_insert.removeClass('d-none');
  clear_quasi();
  rebind();
}

function delete_column(self){
  $(self).parents('.row').remove();
}

function clear_quasi(){
  $('#quasi-form').find('.extra-options').html('');
  $('#quasi-form')[0].reset();
}

function choose_iden(){
  var rows = $('#schema-form').find('.row[data-iden]');
  var idens = new Set();
  var iden = 0;
  $.each(rows, function(i, item){
    idens.add(parseInt($(item).attr('data-iden')));
  });
  for (i = 0; i < rows.length + 1; i++){
    if (!idens.has(i)) {
      iden = i;
      break;
    }
  }
  return iden;
}

$.fn.adjust_form = function(iden, selects_data){
  this.find('button')
    .attr('class','btn btn-outline-danger')
    .attr('onclick','delete_column(this);')
    .html('Delete');
  var labels = this.find('label');
  labels.change_idens(iden,'for');
  var inputs = this.find('input');
  inputs.change_idens(iden,'id');
  inputs.change_idens(iden,'name');
  var selects = this.find('select');
  selects.change_idens(iden,'id');
  selects.adjust_options(selects_data);
}

$.fn.change_idens = function(iden, attr_str){
  $.each(this, function(i, item){
    var prev = $(item).attr(attr_str);
    prev = prev.replaceAll('-ex', '-'+iden);
    $(item).attr(attr_str, prev);
  });

}

$.fn.adjust_options = function(selects_data){
  $.each(this, function(i, item){
    var name_str = $(item).attr('name');
    var value = selects_data[name_str];
    var options = $(item).find('option');
    $.each(options, function(ind, opt){
      if ($(opt).attr('value') == value){
        $(opt).attr('selected','selected');
      }
    });
  });
}

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
