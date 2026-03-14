/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aMG
implements aqz {
    protected int o;
    protected short ekU;
    protected int ejx;
    protected int ekV;
    protected int ekY;

    public int d() {
        return this.o;
    }

    public short coj() {
        return this.ekU;
    }

    public int cmP() {
        return this.ejx;
    }

    public int cok() {
        return this.ekV;
    }

    public int conn() {
        return this.ekY;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ekU = 0;
        this.ejx = 0;
        this.ekV = 0;
        this.ekY = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ekU = aqH2.bGG();
        this.ejx = aqH2.bGI();
        this.ekV = aqH2.bGI();
        this.ekY = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.oAJ.d();
    }
}
