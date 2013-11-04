// how do we know if an object is archived? If the archived viewlet shows up
// we can add a new viewlet that sets the window.object_archived variable
// TODO: add the Unarchive action
function ArchiveDialog(){
    this.install();
}

ArchiveDialog.prototype.install = function(){
    /* Install the Archive transition as an action before the Advanced link */
    var self = this;
    
    var $advanced = $("#workflow-transition-advanced").parent();
    if ($advanced.length === 0){
        var $advanced = $("#workflow-transition-policy").parent();
    }
    var $archive = $advanced.clone();
    if (!window.object_archived) {
        $archive.removeClass('actionSeparator').find('a').attr('id', 'workflow-transition-archive').find('span').text('Archive...');
    } else {
        $archive.removeClass('actionSeparator').find('a').attr('id', 'workflow-transition-unarchive').find('span').text('Unarchive');
    }
    $advanced.before($archive);

    var archive_handler = self.onclick_archive(self);
    $("#workflow-transition-archive").on('click', archive_handler);
    $("#workflow-transition-archive span").on('click', archive_handler);

    var unarchive_handler = self.onclick_unarchive(self);
    $("#workflow-transition-unarchive").on('click', unarchive_handler);
    $("#workflow-transition-unarchive span").on('click', unarchive_handler);
};

ArchiveDialog.prototype.onclick_archive = function(self, e){
    // this is a partial function, it curries the self object
    // it is needed because jquery event object are detached from the OOP object
    if (typeof(e) === "undefined") {
        return function(e){
            self.open_dialog(self);
            return false;
        };
    }
};

ArchiveDialog.prototype.onclick_unarchive = function(self, e){
    // this is a partial function, it curries the self object
    // it is needed because jquery event object are detached from the OOP object
    if (typeof(e) === "undefined") {
        return function(e){
            self.unarchive(self);
            return false;
        };
    }
};

ArchiveDialog.prototype.unarchive = function(){
    var c = confirm("Are you sure you want to unarchive this?");
    if (c) {
        $("#unarchive_object_form").submit();
    }
};

ArchiveDialog.prototype.open_dialog = function(){
    var w = new ArchiveDialog.Window();
    w.open();
};

ArchiveDialog.Window = function(){
    var $target = jQuery("#archive-dialog-target");
    if ($target.length === 0){
        $target = jQuery("<div>").appendTo("body").attr('id', 'archive-dialog-target');
    }
    this.target = $target;
};

ArchiveDialog.Window.prototype.open = function(){
    $("dl.activated").removeClass('activated');
    var self = this;
    self.dialog = jQuery(this.target).dialog({
        title:"Expire/Archive content",
        dialogClass:'archiveDialog',
        modal:true,
        resizable:true,
        width:600,
        height:400,
        open:function(ui){self._open(ui);},
        buttons:{
            'Ok':function(e){self.handle_ok(e);},
        'Cancel':function(e){self.handle_cancel(e);}
        }
    }
    );
};

ArchiveDialog.Window.prototype.handle_cancel = function(e){
    this.dialog.dialog("close");
};

ArchiveDialog.Window.prototype.handle_ok = function(e){
    var self = this;
    jQuery('.notice').remove();
    var workflow_reason = jQuery("input[name='workflow_reasons_radio']:checked").val();
    var hasErrors = false;
    if (!workflow_reason){
        jQuery("#workflow_reason_label").after("<div class='notice' style='color:Black; background-color:#FFE291; " +
                "padding:3px'>Please select reason</div>");
        hasErrors = true;
    }
    if ((workflow_reason === 'other') && (!jQuery("input[name='workflow_other_reason']").val())){
        jQuery("input[name='workflow_other_reason']").after("<div class='notice' style='color:Black; background-color:#FFE291; " +
                "padding:3px'>Please specify reason</div>");
        hasErrors = true;
    }

    if (!jQuery("input[name='workflow_archive_initiator']").val()){
        jQuery("#workflow_initiator_label").after("<div class='notice' style='color:Black; background-color:#FFE291; " +
                "padding:3px'>Please specify initiator</div>");
        hasErrors = true;
    }
    if (hasErrors){
        jQuery(".notice").effect("pulsate", {times:3}, 2000,
                function(){jQuery('.notice').remove();});
        return;
    }
    var $form = jQuery("form", this.target);
    $.post($form.attr('action'), $form.serialize(), function(res){
        self.dialog.dialog("close");
        $("#workflow-transition-archive").remove();
        $.get(context_url+"/@@eea.workflow.archived", function(dom){
            $('.archive_status').remove();
            $("#plone-document-byline").after(dom);
            window.object_archived = true;
            new ArchiveDialog();
        });
    });

    return false;
};

function get_base(){
    var base = (window.context_url || jQuery("base").attr('href') || document.baseURI ||
                window.location.href.split("?")[0].split('@@')[0]);
    return base;
}

ArchiveDialog.Window.prototype._open = function(ui){
    var self = this;

    var base = get_base();
    var url = base + "/archive_dialog";

    jQuery(self.target).load(url, function(){});
};

jQuery(document).ready(function ($) {
    var ad = new ArchiveDialog();
});

