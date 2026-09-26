#ifndef HARMONY_NETWORK_H
#define HARMONY_NETWORK_H
#include <QNetworkRequest>
#include <QUrl>
#include <QByteArray>
#include <QList>
#if QT_CONFIG(ssl)
#include <QSslConfiguration>
#include <QSslCertificate>
#include <QSslSocket>
#endif

inline void harmonyInitializeTls()
{
#if defined(Q_OS_OHOS) && QT_CONFIG(ssl)
    static const bool initialized = [] {
        auto config = QSslConfiguration::defaultConfiguration();
        auto roots = config.caCertificates();
        roots.append(QSslCertificate::fromPath(QStringLiteral(":/certificates/cacert.pem")));
        config.setCaCertificates(roots);
        config.setPeerVerifyMode(QSslSocket::VerifyPeer);
        QSslConfiguration::setDefaultConfiguration(config);
        return true;
    }();
    Q_UNUSED(initialized)
#endif
}

inline bool harmonyValidServiceUrl(const QUrl &url)
{
    return url.isValid() && !url.host().isEmpty() && url.userInfo().isEmpty()
        && (url.scheme() == "https" || url.scheme() == "http") && !url.hasFragment();
}

// Frame complete SSE events as bytes before decoding UTF-8. TCP may split any byte.
class HarmonySseBuffer {
    QByteArray pending, event;
public:
    void clear() { pending.clear(); event.clear(); }
    QList<QByteArray> feed(const QByteArray &bytes) {
        pending += bytes;
        QList<QByteArray> result;
        int end;
        while ((end = pending.indexOf('\n')) >= 0) {
            QByteArray line = pending.left(end);
            pending.remove(0, end + 1);
            if (line.endsWith('\r')) line.chop(1);
            if (line.isEmpty()) {
                if (!event.isEmpty()) { event.chop(1); result.append(event); event.clear(); }
            } else if (line.startsWith("data:")) {
                line.remove(0, 5);
                if (line.startsWith(' ')) line.remove(0, 1);
                event += line + '\n';
            }
        }
        return result;
    }
    bool incomplete() const { return !pending.trimmed().isEmpty() || !event.isEmpty(); }
};
#endif
