/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fuA
implements aqz {
    protected int egM;
    protected int efP;
    protected int dfe;
    protected int[] egL;

    public int tJ() {
        return this.egM;
    }

    public int cjd() {
        return this.efP;
    }

    public int bWc() {
        return this.dfe;
    }

    public int[] cjX() {
        return this.egL;
    }

    @Override
    public void reset() {
        this.egM = 0;
        this.efP = 0;
        this.dfe = 0;
        this.egL = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.egM = aqH2.bGI();
        this.efP = aqH2.bGI();
        this.dfe = aqH2.bGI();
        this.egL = aqH2.bGM();
    }

    @Override
    public final int bGA() {
        return ewj.oAS.d();
    }
}
