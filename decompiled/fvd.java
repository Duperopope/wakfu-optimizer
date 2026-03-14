/*
 * Decompiled with CFR 0.152.
 */
public class fvd
implements aqz {
    protected byte eiC;
    protected int eiD;

    public byte clT() {
        return this.eiC;
    }

    public int clU() {
        return this.eiD;
    }

    @Override
    public void reset() {
        this.eiC = 0;
        this.eiD = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.eiC = aqH2.aTf();
        this.eiD = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        throw new UnsupportedOperationException();
    }
}
