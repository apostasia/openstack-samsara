from samsara.context_aware.interpreter.rules_handlers import base

# Variables
class HostVariables(BaseVariables):

    @numeric_rule_variable
    def current_resource_usage(self):
        value = 0.9
        return value

# Action
class HostActions(BaseActions):

    @rule_action()
    def notify_overload(self):
        print 'overload!'

    @rule_action()
    def notify_underload(self):
        print 'underload!'



class HostRulesHandler(BaseRulesHandler):

        def __init__(self):
            rules = self.load_rules("host.json")

            super(HostRulesHandler,self).__init__(rules,HostVariables(), HostActions())
