/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  ewj
 */
public class fvy
implements aqz {
    protected int o;
    protected short aWL;
    protected short ejA;
    protected long aHT;
    protected long[] asV;
    protected boolean ejB;
    protected boolean ejC;
    protected boolean ejD;
    protected int[] ejE;
    protected int ejF;
    protected String ejG;
    protected short ejH;
    protected int ejI;

    public int d() {
        return this.o;
    }

    public short aVf() {
        return this.aWL;
    }

    public short cmS() {
        return this.ejA;
    }

    public long aqZ() {
        return this.aHT;
    }

    public long[] aGN() {
        return this.asV;
    }

    public boolean cmT() {
        return this.ejB;
    }

    public boolean cmU() {
        return this.ejC;
    }

    public boolean cmV() {
        return this.ejD;
    }

    public int[] cmW() {
        return this.ejE;
    }

    public int cmX() {
        return this.ejF;
    }

    public String cmY() {
        return this.ejG;
    }

    public short cmZ() {
        return this.ejH;
    }

    public int ayQ() {
        return this.ejI;
    }

    @Override
    public void reset() {
        this.o = 0;
        this.aWL = 0;
        this.ejA = 0;
        this.aHT = 0L;
        this.asV = null;
        this.ejB = false;
        this.ejC = false;
        this.ejD = false;
        this.ejE = null;
        this.ejF = 0;
        this.ejG = null;
        this.ejH = 0;
        this.ejI = 0;
    }

    @Override
    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.aWL = aqH2.bGG();
        this.ejA = aqH2.bGG();
        this.aHT = aqH2.bGK();
        this.asV = aqH2.bxz();
        this.ejB = aqH2.bxv();
        this.ejC = aqH2.bxv();
        this.ejD = aqH2.bxv();
        this.ejE = aqH2.bGM();
        this.ejF = aqH2.bGI();
        this.ejG = aqH2.bGL().intern();
        this.ejH = aqH2.bGG();
        this.ejI = aqH2.bGI();
    }

    @Override
    public final int bGA() {
        return ewj.oAD.d();
    }
}
