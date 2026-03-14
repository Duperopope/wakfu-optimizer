/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fyp
implements aqz {
    protected int o;
    protected int euF;
    protected int euG;
    protected short bol;
    protected int euH;
    protected int euI;
    protected int bMn;
    protected String asF;
    protected float euJ;
    protected byte tBy;
    protected int ehX;
    protected int cis;
    protected short rPq;
    protected short rPr;
    protected short cbK;
    protected boolean tBz;

    public int d() {
        return this.o;
    }

    public int cyp() {
        return this.euF;
    }

    public int cyq() {
        return this.euG;
    }

    public short bfd() {
        return this.bol;
    }

    public int cyr() {
        return this.euH;
    }

    public int cys() {
        return this.euI;
    }

    public int getDuration() {
        return this.bMn;
    }

    public String aGr() {
        return this.asF;
    }

    public float cyt() {
        return this.euJ;
    }

    public byte gqr() {
        return this.tBy;
    }

    public int clo() {
        return this.ehX;
    }

    public int eqD() {
        return this.cis;
    }

    public short fRc() {
        return this.rPq;
    }

    public short fRd() {
        return this.rPr;
    }

    public short bst() {
        return this.cbK;
    }

    public boolean gqs() {
        return this.tBz;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.euF = 0;
        this.euG = 0;
        this.bol = 0;
        this.euH = 0;
        this.euI = 0;
        this.bMn = 0;
        this.asF = null;
        this.euJ = 0.0f;
        this.tBy = 0;
        this.ehX = 0;
        this.cis = 0;
        this.rPq = 0;
        this.rPr = 0;
        this.cbK = 0;
        this.tBz = false;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.euF = aqH2.bGI();
        this.euG = aqH2.bGI();
        this.bol = aqH2.bGG();
        this.euH = aqH2.bGI();
        this.euI = aqH2.bGI();
        this.bMn = aqH2.bGI();
        this.asF = aqH2.bGL().intern();
        this.euJ = aqH2.bGH();
        this.tBy = aqH2.aTf();
        this.ehX = aqH2.bGI();
        this.cis = aqH2.bGI();
        this.rPq = aqH2.bGG();
        this.rPr = aqH2.bGG();
        this.cbK = aqH2.bGG();
        this.tBz = aqH2.bxv();
    }

    @Override
    public final int bGA() {
        return ewj.oAG.d();
    }
}
