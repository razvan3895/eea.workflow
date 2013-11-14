/*globals $, window, document, context_url */
$(document).ready(function () {
    "use strict";
    var $archive_action,
        is_minimal,
        $state_menu = $("#plone-contentmenu-workflow"),
        $advanced,
        archive_handler,
        unarchive_handler,
        open_dialog,
        Window,
        install;

    archive_handler = function () {
        open_dialog("archive");
        return false;
    };

    unarchive_handler = function () {
        open_dialog("unarchive");
        return false;
    };

    open_dialog = function (action_type) {
        var w = new Window();
        if (action_type === "archive") {
            w.open_archive();
        } else if (action_type === "unarchive") {
            w.open_unarchive();
        }
    };

    Window = function () {
        var $target = $("#archive-dialog-target"),
            open_archive,
            open_unarchive,
            handle_cancel,
            handle_ok_archive,
            handle_ok_unarchive,
            do_open_archive,
            do_open_unarchive,
            dialog;

        if ($target.length === 0) {
            $target = $("<div>").appendTo("body").attr('id', 'archive-dialog-target');
        }

        open_archive = function () {
            $("dl.activated").removeClass('activated');

            dialog = $target.dialog({
                title: "Expire/Archive content",
                dialogClass: 'archiveDialog',
                modal: true,
                resizable: true,
                width: 600,
                height: 450,
                open: function (ui) { do_open_archive(ui); },
                buttons: {
                    'Ok': function () { handle_ok_archive(); },
                    'Cancel': function () { handle_cancel(); }
                }
            });
        };

        open_unarchive = function () {
            $("dl.activated").removeClass('activated');
            dialog = $target.dialog({
                title: "UnArchive content",
                dialogClass: 'archiveDialog',
                modal: true,
                resizable: true,
                width: 500,
                height: 260,
                open: function (ui) { do_open_unarchive(ui); },
                buttons: {
                    'Ok': function () { handle_ok_unarchive(); },
                    'Cancel': function () { handle_cancel(); }
                }
            });
        };

        handle_cancel = function () {
            dialog.dialog("close");
        };

        handle_ok_archive = function () {
            var $form,
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

            $form = $("form", $target);
            $.post($form.attr('action'), $form.serialize(), function () {
                $('.archive_status').remove();
                dialog.dialog("close");
                $("#workflow-transition-archive").remove();
                $("#archiving_preloader").hide();
                $.get(context_url + "/@@eea.workflow.archived", function (dom) {
                    $("#plone-document-byline").after(dom);
                    window.object_archived = true;
                    install();
                });
            });

            return false;
        };

        handle_ok_unarchive = function () {
            var $form = $("form", $target);
            $("#unarchiving_preloader").show();
            $.post($form.attr('action'), $form.serialize(), function () {
                $("#unarchiving_preloader").remove();
                dialog.dialog("close");
                $("#workflow-transition-unarchive").remove();
                $('.archive_status').remove();
                window.object_archived = false;
                install();
            });

            return false;
        };

        function get_base() {
            var base = (window.context_url || $("base").attr('href') || document.baseURI ||
                        window.location.href.split("?")[0].split('@@')[0]);
            return base;
        }

        do_open_archive = function () {
            var base = get_base(),
                url = base + "/archive_dialog";
            $target.load(url);
        };

        do_open_unarchive = function () {
            var base = get_base(),
                url = base + "/unarchive_dialog";

            $target.load(url);
        };

        return {
            'open_archive': open_archive,
            'open_unarchive': open_unarchive
        };
    };

    install = function () {
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

        $("#workflow-transition-archive").on('click', archive_handler);
        $("#workflow-transition-archive span").on('click', archive_handler);

        $("#workflow-transition-unarchive").on('click', unarchive_handler);
        $("#workflow-transition-unarchive span").on('click', unarchive_handler);
    };

    install();

});
