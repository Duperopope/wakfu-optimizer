/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class aME
implements aqz {
    protected int o;
    protected int egi;
    protected int eld;
    protected int efP;
    protected boolean ele;
    protected short elf;
    protected boolean elg;
    protected int elh;
    protected aMF[] eli;

    public int d() {
        return this.o;
    }

    public int aYs() {
        return this.egi;
    }

    public int cov() {
        return this.eld;
    }

    public int cjd() {
        return this.efP;
    }

    public boolean cow() {
        return this.ele;
    }

    public short cox() {
        return this.elf;
    }

    public boolean coy() {
        return this.elg;
    }

    public int coz() {
        return this.elh;
    }

    public aMF[] coA() {
        return this.eli;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.egi = 0;
        this.eld = 0;
        this.efP = 0;
        this.ele = false;
        this.elf = 0;
        this.elg = false;
        this.elh = 0;
        this.eli = null;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.egi = aqH2.bGI();
        this.eld = aqH2.bGI();
        this.efP = aqH2.bGI();
        this.ele = aqH2.bxv();
        this.elf = aqH2.bGG();
        this.elg = aqH2.bxv();
        this.elh = aqH2.bGI();
        int n = aqH2.bGI();
        this.eli = new aMF[n];
        for (int i = 0; i < n; ++i) {
            this.eli[i] = new aMF();
            this.eli[i].a(aqH2);
        }
    }

    @Override
    public final int bGA() {
        return ewj.oAp.d();
    }
}
