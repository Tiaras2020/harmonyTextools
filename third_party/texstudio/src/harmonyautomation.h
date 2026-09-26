#ifndef HARMONY_AUTOMATION_H
#define HARMONY_AUTOMATION_H
#include <QTcpServer>
#include <QTcpSocket>
#include <QJsonDocument>
#include <QJsonObject>
#include <QTimer>
#include <QUuid>
#include <functional>

// One bounded JSON request per connection; loopback only, opt-in per session.
class HarmonyAutomation : public QTcpServer {
public:
    QString token = QUuid::createUuid().toString(QUuid::WithoutBraces)
        + QUuid::createUuid().toString(QUuid::WithoutBraces);
    std::function<QJsonObject(const QJsonObject &)> dispatch;
    explicit HarmonyAutomation(QObject *parent = nullptr) : QTcpServer(parent) {
        setMaxPendingConnections(4);
        connect(this, &QTcpServer::newConnection, this, [this]() {
            while (hasPendingConnections()) {
                QTcpSocket *socket = nextPendingConnection();
                socket->setReadBufferSize(8193);
                connect(socket, &QTcpSocket::disconnected, socket, &QObject::deleteLater);
                QTimer::singleShot(5000, socket, [socket]() { socket->abort(); });
                connect(socket, &QTcpSocket::readyRead, this, [this, socket]() {
                    if (socket->property("answered").toBool()) return;
                    if (!socket->canReadLine()) {
                        if (socket->bytesAvailable() > 8192) socket->abort();
                        return;
                    }
                    socket->setProperty("answered", true);
                    QJsonParseError error;
                    const auto document = QJsonDocument::fromJson(socket->readLine(8193), &error);
                    const auto request = document.object();
                    QJsonObject reply;
                    if (error.error != QJsonParseError::NoError || !document.isObject())
                        reply = {{"ok", false}, {"error", "invalid_json"}};
                    else if (request.value("token").toString() != token)
                        reply = {{"ok", false}, {"error", "unauthorized"}};
                    else if (dispatch) reply = dispatch(request);
                    else reply = {{"ok", false}, {"error", "unavailable"}};
                    socket->write(QJsonDocument(reply).toJson(QJsonDocument::Compact) + '\n');
                    socket->disconnectFromHost();
                });
            }
        });
    }
    bool start() { return listen(QHostAddress::LocalHost, 0); }
};
#endif
