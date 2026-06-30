import addonHandler
import globalPluginHandler


addonHandler.initTranslation()


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = _("Clipboard Insight")
