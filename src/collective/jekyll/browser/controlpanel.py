from zope.interface import implements
from zope.component import adapts
from zope.component import getUtility
from zope.formlib import form
from zope.schema.interfaces import IVocabularyFactory

from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.registry.interfaces import IRegistry
try:
    from plone.app.controlpanel.form import ControlPanelForm
    from plone.app.controlpanel.widgets import MultiCheckBoxThreeColumnWidget

    HAVE_PLONE5 = False
except:
    from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
    from plone.app.registry.browser.controlpanel import RegistryEditForm as ControlPanelForm
    from plone.z3cform import layout
    HAVE_PLONE5 = True


from collective.jekyll import jekyllMessageFactory as _
from collective.jekyll.interfaces import IJekyllSettings


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

    form_fields = not HAVE_PLONE5 and form.FormFields(IJekyllSettings)
    schema = HAVE_PLONE5 and IJekyllSettings

    @property
    def active_symptoms(self,):
        if not HAVE_PLONE5:
            active_symptoms = form_fields['activeSymptoms']
            active_symptoms.custom_widget = MultiCheckBoxThreeColumnWidget
            active_symptoms.custom_widget.cssClass = 'label'
        else:
            active_symptoms = None
        return active_symptoms
    """
    _active_symptoms = not HAVE_PLONE5 and form_fields['activeSymptoms'] or Fake(
    )
    _active_symptoms.custom_widget = not HAVE_PLONE5 and MultiCheckBoxThreeColumnWidget or Fake()
    _active_symptoms.custom_widget.cssClass = 'label'
    """


if HAVE_PLONE5:
    WrappedJekyllControlPanel = layout.wrap_form(
        JekyllControlPanel, ControlPanelFormWrapper)
