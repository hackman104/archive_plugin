from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.urlresolvers import reverse

from plugins.disqus import forms
from plugins.disqus import plugin_settings

from utils import setting_handler
from utils import models

from submission.models import Article
from journal.models import Issue
from models import Version

def index(request):
    """
    Creates the admin page for turning the plugin's elements on or off
    """
    plugin = models.Plugin.objects.get(name=plugin_settings.SHORT_NAME)
    
    journal_archive_enabled = setting_handler.get_plugin_setting(plugin, 'journal_archive_enabled', request.journal, create=True,
                                                        pretty='Enable Journal Archive Display', types='boolean').processed_value
    article_archive_enabled = setting_handler.get_plugin_setting(plugin, 'article_archive_enabled', request.journal, create=True,
                                                        pretty='Enable Article Archive Display', types='boolean').processed_value
    edit_article_enabled = setting_handler.get_plugin_setting(plugin, 'edit_archive_enabled', request.journal, create=True,
                                                        pretty='Enable Article Editing and Updating', types='boolean').processed_value
    
    admin_form = forms.ArchiveAdminForm(initial={'journal_archive_enabled': journal_archive_enabled, 
                                                'article_archive_enabled': article_archive_enabled,
                                                'edit_article_enabled': edit_article_enabled})

    if request.POST:
        admin_form = forms.ArchiveAdminForm(request.POST)

        if admin_form.is_valid():
            for setting_name, setting_value in admin_form.cleaned_data.items():
                setting_handler.save_plugin_setting(plugin, setting_name, setting_value, request.journal)
                messages.add_message(request, messages.SUCCESS, '{0} setting updated.'.format(setting_name))

            return redirect(reverse('archive_index'))

    template = "archive_plugin/index.html"
    context = {
        'admin_form': admin_form,
    }

    return render(request, template, context)


def view_archive(request):
    pass
    # TODO: write logic for querying database, viewing the relevant archived version of journal or article
    # may need to write two versions of function based on whether viewing archived version of article or journal

def journal_archive(request):
    """
    Display list of overall journal archives
    """
    journal_versions = Issue.objects.filter(journal=request.journal).order_by('-date')
    context = {'journal_versions': journal_versions}
    template = "archive_plugin/journal_version_list.html"

    return render(request, template, context)

def article_archive(request, article_id):
    """
    :article_id = an int representing the pk of the article requested
    Displays a list of previous version of an article
    """
    article = Article.objects.get(pk=article_id)
    base_article = Article.objects.get(pk=article.version.orig_article)

    # need to deal with possibility update for article has been submitted but not published
    versions = Article.objects.filter(version__orig_article=base_article.pk).order_by('-date_published')
    # versions = base_article.version_set.all()

    template = "archive_plugin/article_version_list.html"
    context = {'main_article': base_article, 'versions': versions}

    return render(request, template, context)

def update_article(request, article_id):
    """
    Starts the process for authors to submit updates to an existing article
    """
    pass


# use utils.notify_helpers function send_email_with_body_from_user(request, subject, to, body, log_dict=None) to email user about update request
# article.authors is many to many - article.authors.all() or use article.owner?