/*
 * Decompiled with CFR 0.152.
 */
import java.util.HashMap;

public class aOy {
    protected int emS;
    protected HashMap<Integer, aOz> esr;
    protected float erN;
    protected float erO;
    protected float erP;
    protected float erQ;
    protected float erR;
    protected float erS;
    protected float erV;
    protected float ess;
    protected float erT;
    protected float erU;
    protected boolean est;
    protected boolean esu;
    protected boolean esv;
    protected boolean esw;
    protected float esx;
    protected float esy;
    protected float esz;
    protected float esA;
    protected boolean esB;
    protected boolean esC;
    protected boolean esD;
    protected boolean esm;

    public int cqq() {
        return this.emS;
    }

    public HashMap<Integer, aOz> cvT() {
        return this.esr;
    }

    public float cvp() {
        return this.erN;
    }

    public float cvq() {
        return this.erO;
    }

    public float cvr() {
        return this.erP;
    }

    public float cvs() {
        return this.erQ;
    }

    public float cvt() {
        return this.erR;
    }

    public float cvu() {
        return this.erS;
    }

    public float cvx() {
        return this.erV;
    }

    public float cvU() {
        return this.ess;
    }

    public float cvv() {
        return this.erT;
    }

    public float cvw() {
        return this.erU;
    }

    public boolean cvV() {
        return this.est;
    }

    public boolean cvW() {
        return this.esu;
    }

    public boolean cvX() {
        return this.esv;
    }

    public boolean cvY() {
        return this.esw;
    }

    public float cvZ() {
        return this.esx;
    }

    public float cwa() {
        return this.esy;
    }

    public float cwb() {
        return this.esz;
    }

    public float cwc() {
        return this.esA;
    }

    public boolean cwd() {
        return this.esB;
    }

    public boolean cwe() {
        return this.esC;
    }

    public boolean cwf() {
        return this.esD;
    }

    public boolean cvO() {
        return this.esm;
    }

    public void a(aqH aqH2) {
        this.emS = aqH2.bGI();
        int n = aqH2.bGI();
        this.esr = new HashMap(n);
        for (int i = 0; i < n; ++i) {
            int n2 = aqH2.bGI();
            aOz aOz2 = new aOz();
            aOz2.a(aqH2);
            this.esr.put(n2, aOz2);
        }
        this.erN = aqH2.bGH();
        this.erO = aqH2.bGH();
        this.erP = aqH2.bGH();
        this.erQ = aqH2.bGH();
        this.erR = aqH2.bGH();
        this.erS = aqH2.bGH();
        this.erV = aqH2.bGH();
        this.ess = aqH2.bGH();
        this.erT = aqH2.bGH();
        this.erU = aqH2.bGH();
        this.est = aqH2.bxv();
        this.esu = aqH2.bxv();
        this.esv = aqH2.bxv();
        this.esw = aqH2.bxv();
        this.esx = aqH2.bGH();
        this.esy = aqH2.bGH();
        this.esz = aqH2.bGH();
        this.esA = aqH2.bGH();
        this.esB = aqH2.bxv();
        this.esC = aqH2.bxv();
        this.esD = aqH2.bxv();
        this.esm = aqH2.bxv();
    }
}
