/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvK
implements aqz {
    protected int o;
    protected short ekp;
    protected short ekq;
    protected int[] ekr;

    public int d() {
        return this.o;
    }

    public short cnD() {
        return this.ekp;
    }

    public short cnE() {
        return this.ekq;
    }

    public int[] cnF() {
        return this.ekr;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ekp = 0;
        this.ekq = 0;
        this.ekr = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ekp = aqH2.bGG();
        this.ekq = aqH2.bGG();
        this.ekr = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oAP.d();
    }
}
