/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fwc
implements aqz {
    protected int o;
    protected short ekU;
    protected int elk;
    protected int ell;
    protected long elm;
    protected byte asH;

    public int d() {
        return this.o;
    }

    public short coj() {
        return this.ekU;
    }

    public int coC() {
        return this.elk;
    }

    public int coD() {
        return this.ell;
    }

    public long coE() {
        return this.elm;
    }

    public byte aGu() {
        return this.asH;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.ekU = 0;
        this.elk = 0;
        this.ell = 0;
        this.elm = 0L;
        this.asH = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.ekU = aqH2.bGG();
        this.elk = aqH2.bGI();
        this.ell = aqH2.bGI();
        this.elm = aqH2.bGK();
        this.asH = aqH2.aTf();
    }

    @Override
    public final int bGA() {
        return ewj.oAo.d();
    }
}
