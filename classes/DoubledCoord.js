exports.OffsetCoord = OffsetCoord;

OffsetCoord.EVEN = 1;
OffsetCoord.ODD = -1;

class DoubledCoord {
        constructor(col, row) {
            this.col = col;
            this.row = row;
        }
        static qdoubledFromCube(h) {
            var col = h.q;
            var row = 2 * h.r + h.q;
            return new DoubledCoord(col, row);
        }
        qdoubledToCube() {
            var q = this.col;
            var r = (this.row - this.col) / 2;
            var s = -q - r;
            return new Hex(q, r, s);
        }
        static rdoubledFromCube(h) {
            var col = 2 * h.q + h.r;
            var row = h.r;
            return new DoubledCoord(col, row);
        }
        rdoubledToCube() {
            var q = (this.col - this.row) / 2;
            var r = this.row;
            var s = -q - r;
            return new Hex(q, r, s);
        }
    }