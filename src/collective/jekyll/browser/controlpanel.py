# -*- coding: utf-8 -*-
from collective.jekyll import jekyllMessageFactory as _
from collective.jekyll.interfaces import IJekyllSettings
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.registry.interfaces import IRegistry
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
try:
    from plone.app.controlpanel.form import ControlPanelForm
    from plone.app.controlpanel.widgets import MultiCheckBoxThreeColumnWidget

    HAVE_PLONE5 = False
except ImportError:
    from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
    from plone.app.registry.browser.controlpanel import RegistryEditForm as ControlPanelForm
    from plone.z3cform import layout
    from z3c.form.field import Fields
    from z3c.form.browser.checkbox import CheckBoxFieldWidget
    HAVE_PLONE5 = True


class JekyllControlPanelAdapter(SchemaAdapterBase):

    adapts(IPloneSiteRoot)
    implements(IJekyllSettings)

    def __init__(self, context):
        super(JekyllControlPanelAdapter, self).__init__(context)
        registry = getUtility(IRegistry)
        self.settings = registry.forInterface(IJekyllSettings, False)
        vocabFactory = getUtility(IVocabularyFactory,
                                  name="collective.jekyll.SymptomsVocabulary")
        self.symptoms = vocabFactory(context)

    def getActiveSymptoms(self):
        if self.settings.activeSymptoms is None:
            return [s.value for s in self.symptoms]

        activeSymptoms = []
        for symptom in self.symptoms:
            if symptom.value in self.settings.activeSymptoms:
                activeSymptoms.append(symptom.value)
        return activeSymptoms

    def setActiveSymptoms(self, value):
        self.settings.activeSymptoms = value

    activeSymptoms = property(getActiveSymptoms,
                              setActiveSymptoms)


class JekyllControlPanel(ControlPanelForm):

    label = _("Content quality")
    description = _(
        "You can activate / deactivate symptoms using this form.")
    form_name = _("Symptoms activation")

    @property
    def form_fields(self,):
        """ formlib for plone4
        """
        if not HAVE_PLONE5:
            fields = form.FormFields(IJekyllSettings)
            active_symptoms = fields['activeSymptoms']
            active_symptoms.custom_widget = MultiCheckBoxThreeColumnWidget
            active_symptoms.custom_widget.cssClass = 'label'
            return fields

    @property
    def schema(self,):
        # plone autoform and plone5
        return IJekyllSettings

    def updateFields(self,):
        # plone autoform and plone5
        super(JekyllControlPanel, self).updateFields()
        if not HAVE_PLONE5:
            return

        self.fields['activeSymptoms'].widgetFactory = CheckBoxFieldWidget


if HAVE_PLONE5:
    WrappedJekyllControlPanel = layout.wrap_form(
        JekyllControlPanel, ControlPanelFormWrapper)

