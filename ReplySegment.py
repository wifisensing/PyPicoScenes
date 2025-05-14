import cppyy

cppyy.cppdef("""
#include <functional>
#include <map>
#include <PicoScenes/PicoScenesCommons.hxx>
#include <PicoScenes/AbstractPicoScenesFrameSegment.hxx>

enum class RTTFrameType : uint16_t {
    RTTInitiation = 1000,
    ReplyStart,
    ReplyEnd,
};

struct Reply {
    int64_t lastRxTime;
    int64_t lastTxTime;
    std::vector<uint8_t> toBuffer(){
        return std::vector<uint8_t>{reinterpret_cast<uint8_t *>(this), reinterpret_cast<uint8_t *>(this) + sizeof(Reply)};
    }

} __attribute__ ((__packed__));

class ReplySegment : public AbstractPicoScenesFrameSegment {
public:
    ReplySegment();

    explicit ReplySegment(const Reply &info);

    ReplySegment(const uint8_t *buffer, uint32_t bufferLength);

    [[nodiscard]] const Reply &getReply() const;

    void setReply(const Reply &reply);

    [[nodiscard]] std::string toString() const override;

private:
    static std::map<uint16_t, std::function<Reply(const uint8_t *, uint32_t)>> versionedSolutionMap;

    static std::map<uint16_t, std::function<Reply(const uint8_t *, uint32_t)>> initializeSolutionMap() noexcept;

    Reply reply{};
};

static auto v1Parser = [](const uint8_t* buffer, const uint32_t bufferLength) -> Reply {
    uint32_t pos = 0;
    if (bufferLength < sizeof(Reply))
        throw std::runtime_error("ReplySegment v1Parser cannot parse the segment with insufficient buffer length.");

    auto r = Reply();
    r.lastRxTime = *reinterpret_cast<const int64_t *>(buffer + pos);
    pos += 8;
    r.lastTxTime = *reinterpret_cast<const int64_t *>(buffer + pos);
    pos += 8;
    if (pos != bufferLength)
        throw std::runtime_error("ReplySegment v1Parser cannot parse the segment with mismatched buffer length.");

    return r;
};

std::map<uint16_t, std::function<Reply(const uint8_t*, uint32_t)>> ReplySegment::versionedSolutionMap = initializeSolutionMap();

std::map<uint16_t, std::function<Reply(const uint8_t*, uint32_t)>> ReplySegment::initializeSolutionMap() noexcept {
    std::map<uint16_t, std::function<Reply(const uint8_t*, uint32_t)>> map {{0x1U, v1Parser}};
    return map;
}

ReplySegment::ReplySegment() : AbstractPicoScenesFrameSegment("Reply", 0x1U) {
}

ReplySegment::ReplySegment(const Reply& replyV) : ReplySegment() {
    setReply(replyV);
}

ReplySegment::ReplySegment(const uint8_t* buffer, uint32_t bufferLength) : AbstractPicoScenesFrameSegment(buffer, bufferLength) {
    if (segmentName != "Reply")
        throw std::runtime_error("ReplySegment cannot parse the segment named " + segmentName + ".");
    if (!versionedSolutionMap.contains(segmentVersionId))
        throw std::runtime_error("ReplySegment cannot parse the segment with version v" + std::to_string(segmentVersionId) + ".");

    reply = versionedSolutionMap.at(segmentVersionId)(segmentPayload.data(), segmentPayload.size());
}

std::string ReplySegment::toString() const {
    return AbstractPicoScenesFrameSegment::toString();
}

const Reply& ReplySegment::getReply() const {
    return reply;
}

void ReplySegment::setReply(const Reply& replyV) {
    reply = replyV;
    setSegmentPayload(reply.toBuffer());
}         
""")
