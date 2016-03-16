var contactcontactmailsend = {};

contactcontactmailsend.init = function(){
    jQuery(document).bind('loadInsideOverlay', function(e, el, responseText, errorText, api) {
        var overlay = $(el).closest('.overlay-ajax');
        var form = jQuery(overlay).find('#form');
        if(form.hasClass("kssattr-formname-mail_selection")){
            var uids = contactfacetednav.contacts.selection_uids();
            var field = jQuery(overlay).find('#formfield-form-widgets-template').first()
            contactcontactmailsend.populate_hidden_field(field, uids);
        };
     });
};

contactcontactmailsend.facetednav_send_mail = function() {
    var url = portal_url + '/@@mail_selection';
    contactcontactmailsend._facetednav_open_overlay(url);
};

contactcontactmailsend._facetednav_open_overlay = function(url){
    jQuery("<a href='" + url + "'>Edit</a>'").prepOverlay({
        subtype:'ajax',
        filter: common_content_filter,
        formselector: '#form',
        closeselector: '[name="form.buttons.cancel"]',
        noform: function(el, pbo){
            contactfacetednav.store_overlay_messages(el);
            Faceted.Form.do_form_query();
            jQuery('.faceted-contactlist-widget').each(function(){
                var widget = jQuery(this);
                var sortcountable = widget.hasClass('faceted-sortcountable');
                Faceted.Widgets[this.id.split('_')[0]].count(sortcountable);
            });
            return 'close';
        }
    }).click();
};

contactcontactmailsend.populate_hidden_field = function(field, uids){
    for(var num in uids){
        var uid = uids[num];
        var input = jQuery('<input type="hidden" value="' + uid + '" class="hidden-widget" name="UID:list" originalvalue="' + uid +'"/>');
        field.append(input);
    }
};

jQuery(document).ready(contactcontactmailsend.init);