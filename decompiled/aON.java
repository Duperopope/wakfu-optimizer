/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aON
implements aqz {
    protected int o;
    protected int atn;
    protected int ciZ;
    protected boolean euE;
    protected int[] egL;

    public int d() {
        return this.o;
    }

    public int aHp() {
        return this.atn;
    }

    public int aVt() {
        return this.ciZ;
    }

    public boolean cyo() {
        return this.euE;
    }

    public int[] cjX() {
        return this.egL;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.atn = 0;
        this.ciZ = 0;
        this.euE = false;
        this.egL = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.atn = aqH2.bGI();
        this.ciZ = aqH2.bGI();
        this.euE = aqH2.bxv();
        this.egL = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.ozK.d();
    }
}
