/*
 * Decompiled with CFR 0.152.
 * 
 * Could not load the following classes:
 *  aqH
 *  aqz
 *  ewj
 */
public class aOB
implements aqz {
    protected int o;
    protected short aWK;
    protected int[] esI;
    protected int[] aNh;
    protected int[] esJ;
    protected boolean esK;
    protected boolean esL;
    protected boolean esM;
    protected boolean esN;
    protected String esO;
    protected String esP;
    protected boolean esQ;
    protected boolean bfZ;
    protected boolean esR;
    protected int[] egL;
    protected int[] esS;
    protected boolean esT;
    protected boolean esU;
    protected byte esV;
    protected byte esW;
    protected boolean esX;
    protected boolean esY;
    protected String bds;
    protected boolean esZ;
    protected short atb;

    public int d() {
        return this.o;
    }

    public short aVe() {
        return this.aWK;
    }

    public int[] cwk() {
        return this.esI;
    }

    public int[] aQN() {
        return this.aNh;
    }

    public int[] cwl() {
        return this.esJ;
    }

    public short cwm() {
        return (short)this.aNh[0];
    }

    public int cwn() {
        return this.aNh.length == 0 ? 0 : 1000 * this.aNh[1];
    }

    public int cwo() {
        return this.esJ[0];
    }

    public int cwp() {
        return this.esJ.length == 0 ? 0 : 1000 * this.esJ[1];
    }

    public boolean cwq() {
        return this.esK;
    }

    public boolean cwr() {
        return this.esL;
    }

    public boolean cws() {
        return this.esM;
    }

    public boolean cwt() {
        return this.esN;
    }

    public String cwu() {
        return this.esO;
    }

    public String cwv() {
        return this.esP;
    }

    public boolean cww() {
        return this.esQ;
    }

    public boolean aZW() {
        return this.bfZ;
    }

    public boolean cwx() {
        return this.esR;
    }

    public int[] cjX() {
        return this.egL;
    }

    public int[] cwy() {
        return this.esS;
    }

    public boolean cwz() {
        return this.esT;
    }

    public boolean cwA() {
        return this.esU;
    }

    public byte cwB() {
        return this.esV;
    }

    public byte cwC() {
        return this.esW;
    }

    public boolean cwD() {
        return this.esX;
    }

    public boolean cwE() {
        return this.esY;
    }

    public String aXE() {
        return this.bds;
    }

    public boolean cwF() {
        return this.esZ;
    }

    public short aHb() {
        return this.atb;
    }

    public void reset() {
        this.o = 0;
        this.aWK = 0;
        this.esI = null;
        this.aNh = null;
        this.esJ = null;
        this.esK = false;
        this.esL = false;
        this.esM = false;
        this.esN = false;
        this.esO = null;
        this.esP = null;
        this.esQ = false;
        this.bfZ = false;
        this.esR = false;
        this.egL = null;
        this.esS = null;
        this.esT = false;
        this.esU = false;
        this.esV = 0;
        this.esW = 0;
        this.esX = false;
        this.esY = false;
        this.bds = null;
        this.esZ = false;
        this.atb = 0;
    }

    public void a(aqH aqH2) {
        this.o = aqH2.bGI();
        this.aWK = aqH2.bGG();
        this.esI = aqH2.bGM();
        this.aNh = aqH2.bGM();
        this.esJ = aqH2.bGM();
        this.esK = aqH2.bxv();
        this.esL = aqH2.bxv();
        this.esM = aqH2.bxv();
        this.esN = aqH2.bxv();
        this.esO = aqH2.bGL().intern();
        this.esP = aqH2.bGL().intern();
        this.esQ = aqH2.bxv();
        this.bfZ = aqH2.bxv();
        this.esR = aqH2.bxv();
        this.egL = aqH2.bGM();
        this.esS = aqH2.bGM();
        this.esT = aqH2.bxv();
        this.esU = aqH2.bxv();
        this.esV = aqH2.aTf();
        this.esW = aqH2.aTf();
        this.esX = aqH2.bxv();
        this.esY = aqH2.bxv();
        this.bds = aqH2.bGL().intern();
        this.esZ = aqH2.bxv();
        this.atb = aqH2.bGG();
    }

    public final int bGA() {
        return ewj.ozE.d();
    }
}
