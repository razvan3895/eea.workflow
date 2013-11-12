/*globals $, window, document, context_url */

function ArchiveDialog() {
    this.install();
}

ArchiveDialog.prototype.install = function () {
    /* Install the Archive transition as an action before the Advanced link */
    var self = this,
        $archive_action,
        is_minimal,
        $state_menu = $("#plone-contentmenu-workflow"),
        $advanced,
        archive_handler,
        unarchive_handler;
    if ($state_menu.length === 0) {
        return;
    }

    if (!window.object_archived) {
        $archive_action = $("<a>").attr({href: '#', "id": "workflow-transition-archive"}).html("<span class='subMenuTitle'>Archive...</span>");
    } else {
        $archive_action = $("<a>").attr({href: '#', "id": "workflow-transition-unarchive"}).html("<span class='subMenuTitle'>UnArchive...</span>");
    }

    is_minimal = $state_menu.find("dd").length;
    if (is_minimal === 0) {
        $("#contentActionMenus").prepend(
            $("<dl>").addClass("actionMenu deactivated").append(
                $("<dt>").addClass("actionMenuHeader").append(
                    $("<span>").append($archive_action)
                )
            )
        );
    } else {
        $advanced = $("#workflow-transition-advanced").parent();
        if ($advanced.length === 0) {
            $advanced = $("#workflow-transition-policy").parent();
        }
        $advanced.before($("<li>").append($archive_action));
    }

    archive_handler = self.onclick_archive(self);
    $("#workflow-transition-archive").on('click', archive_handler);
    $("#workflow-transition-archive span").on('click', archive_handler);

    unarchive_handler = self.onclick_unarchive(self);
    $("#workflow-transition-unarchive").on('click', unarchive_handler);
    $("#workflow-transition-unarchive span").on('click', unarchive_handler);
};

ArchiveDialog.prototype.onclick_archive = function (self, e) {
    // this is a partial function, it curries the self object
    // it is needed because jquery event object are detached from the OOP object
    if (e === undefined) {
        return function () {
            self.open_dialog("archive");
            return false;
        };
    }
};

ArchiveDialog.prototype.onclick_unarchive = function (self, e) {
    // this is a partial function, it curries the self object
    // it is needed because jquery event object are detached from the OOP object
    if (e === undefined) {
        return function () {
            self.open_dialog("unarchive");
            return false;
        };
    }
};

ArchiveDialog.prototype.open_dialog = function (action_type) {
    var w = new ArchiveDialog.Window();
    switch (action_type) {
    case "archive":
        w.open_archive();
        break;
    case "unarchive":
        w.open_unarchive();
        break;
    }
};

ArchiveDialog.Window = function () {
    var $target = $("#archive-dialog-target");
    if ($target.length === 0) {
        $target = $("<div>").appendTo("body").attr('id', 'archive-dialog-target');
    }
    this.target = $target;
};

ArchiveDialog.Window.prototype.open_archive = function () {
    $("dl.activated").removeClass('activated');
    var self = this;
    self.dialog = $(this.target).dialog({
        title: "Expire/Archive content",
        dialogClass: 'archiveDialog',
        modal: true,
        resizable: true,
        width: 600,
        height: 450,
        open: function (ui) { self._open_archive(ui); },
        buttons: {
            'Ok': function (e) { self.handle_ok_archive(e); },
            'Cancel': function (e) { self.handle_cancel(e); }
        }
        }
        );
};

ArchiveDialog.Window.prototype.open_unarchive = function () {
    $("dl.activated").removeClass('activated');
    var self = this;
    self.dialog = $(this.target).dialog({
        title: "UnArchive content",
        dialogClass: 'archiveDialog',
        modal: true,
        resizable: true,
        width: 500,
        height: 260,
        open: function (ui) { self._open_unarchive(ui); },
        buttons: {
            'Ok': function (e) { self.handle_ok_unarchive(e); },
            'Cancel': function (e) { self.handle_cancel(e); }
        }
        }
        );
};

ArchiveDialog.Window.prototype.handle_cancel = function () {
    this.dialog.dialog("close");
};

ArchiveDialog.Window.prototype.handle_ok_archive = function () {
    var self = this,
        $form,
        workflow_reason = $("input[name='workflow_reasons_radio']:checked").val(),
        hasErrors = false;
    $('.notice').remove();
    if (!workflow_reason) {
        $("#workflow_reason_label").after("<div class='notice' style='color:Black; background-color:#FFE291; " +
                "padding:3px'>Please select reason</div>");
        hasErrors = true;
    }
    if ((workflow_reason === 'other') && (!$("input[name='workflow_other_reason']").val())) {
        $("input[name='workflow_other_reason']").after("<div class='notice' style='color:Black; background-color:#FFE291; " +
                "padding:3px'>Please specify reason</div>");
        hasErrors = true;
    }

    if (!$("input[name='workflow_archive_initiator']").val()) {
        $("#workflow_initiator_label").after("<div class='notice' style='color:Black; background-color:#FFE291; " +
                "padding:3px'>Please specify initiator</div>");
        hasErrors = true;
    }
    if (hasErrors) {
        $(".notice").effect("pulsate", {times: 3}, 2000,
                function () { $('.notice').remove(); });
        return;
    }
    $("#archiving_preloader").show();

    $form = $("form", this.target);
    $.post($form.attr('action'), $form.serialize(), function () {
        $('.archive_status').remove();
        self.dialog.dialog("close");
        $("#workflow-transition-archive").remove();
        $("#archiving_preloader").hide();
        $.get(context_url + "/@@eea.workflow.archived", function (dom) {
            $("#plone-document-byline").after(dom);
            window.object_archived = true;
            new ArchiveDialog();
        });
    });

    return false;
};

ArchiveDialog.Window.prototype.handle_ok_unarchive = function () {
    var self = this,
        $form = $("form", this.target);
    $("#unarchiving_preloader").show();
    $.post($form.attr('action'), $form.serialize(), function () {
        $("#unarchiving_preloader").remove();
        self.dialog.dialog("close");
        $("#workflow-transition-unarchive").remove();
        $('.archive_status').remove();
        window.object_archived = false;
        new ArchiveDialog();
    });

    return false;
};

function get_base() {
    var base = (window.context_url || $("base").attr('href') || document.baseURI ||
                window.location.href.split("?")[0].split('@@')[0]);
    return base;
}

ArchiveDialog.Window.prototype._open_archive = function () {
    var self = this,
        base = get_base(),
        url = base + "/archive_dialog";

    $(self.target).load(url);
};

ArchiveDialog.Window.prototype._open_unarchive = function () {
    var self = this,
        base = get_base(),
        url = base + "/unarchive_dialog";

    $(self.target).load(url);
};

$(document).ready(function () {
    var ad = new ArchiveDialog();
});

