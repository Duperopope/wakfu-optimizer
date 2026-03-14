/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aNk
implements aqz {
    protected int o;
    protected byte emX;
    protected aNl[] emY;

    public int d() {
        return this.o;
    }

    public byte cqv() {
        return this.emX;
    }

    public aNl[] cqw() {
        return this.emY;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.emX = 0;
        this.emY = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.emX = aqH2.aTf();
        int n = aqH2.bGI();
        this.emY = new aNl[n];
        for (int i = 0; i < n; ++i) {
            this.emY[i] = new aNl();
            this.emY[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAH.d();
    }
}
