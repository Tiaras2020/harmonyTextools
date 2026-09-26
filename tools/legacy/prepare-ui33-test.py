from pathlib import Path
r=Path('/mnt/e/CodeProjects/harmonytexlive');src=r/'texstudio-harmony/third_party/texstudio/src';out=r/'validation/workbench-1.0.33'
t=(src/'harmonyaiworkbench.h').read_text();t=t.replace('#include "configmanager.h"','#include "mock-config.h"').replace('class HarmonyAiWorkbench : public QWidget {','class HarmonyAiWorkbench : public QWidget {\npublic:');(out/'tested-workbench.h').write_text(t)
(out/'mock-config.h').write_text('''#include <QtCore>
struct ConfigManager {QString configBaseDir,ai_apiurl,ai_apikey,ai_preferredModel,ai_systemPrompt;bool ai_recordConversation=false;int ai_provider=0;};
''')
