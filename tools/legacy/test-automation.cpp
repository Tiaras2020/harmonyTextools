#include "harmonyautomation.h"
#include <QCoreApplication>
#include <QFile>
int main(int argc, char **argv) {
    QCoreApplication app(argc, argv);
    if (argc != 2) return 2;
    HarmonyAutomation server;
    if (!server.start()) return 3;
    server.dispatch = [](const QJsonObject &request) {
        if (request.value("command") == "status") return QJsonObject{{"ok", true}, {"state", "idle"}};
        return QJsonObject{{"ok", false}, {"error", "unsupported_command"}};
    };
    QFile file(argv[1]);
    if (!file.open(QIODevice::WriteOnly)) return 4;
    file.write(QJsonDocument(QJsonObject{{"protocol", 1}, {"host", "127.0.0.1"},
        {"port", int(server.serverPort())}, {"token", server.token}}).toJson());
    file.close();
    QTimer::singleShot(30000, &app, &QCoreApplication::quit);
    return app.exec();
}
