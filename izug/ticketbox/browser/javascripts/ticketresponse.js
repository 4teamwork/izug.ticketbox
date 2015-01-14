$(document).on('ready reload', function() {
  $('select[name=responsibleManager]').select2({dropdownAutoWidth: 'true'});
  $('select[name=issuer]').select2({dropdownAutoWidth: 'true'});
  $('select[name=variety]').select2({dropdownAutoWidth: 'true'});
  $('select[name=area]').select2({dropdownAutoWidth: 'true'});
});
